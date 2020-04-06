import logging

from django.views.generic import TemplateView, DetailView, FormView, ListView
from django.shortcuts import HttpResponseRedirect, HttpResponse, redirect
from django.http import JsonResponse
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.db.models import Q

from braces.views import LoginRequiredMixin
from notifications.models import Notification
from notifications.signals import notify
from notifications.views import AllNotificationsList, UnreadNotificationsList

from .mixins import FrontendMixin, CreateMixin
from .models import *
from .forms import TestimonialForm, ContactForm

from accounts.models import Member


logger = logging.getLogger(__name__)


class HomePage(FrontendMixin, TemplateView):
    template_name = "frontend/index.html"

    def dispatch(self, request, *args, **kwargs):
        """
            Dispatch function gets called first when the view is triggered
            Other functions of the view are only called after the successful execution
            of dispatch function
        """
        if request.user.is_authenticated and not request.user.is_superuser:
            user = Member.objects.get(username=self.request.user)
            if not user.first_name or not user.last_name:
                return HttpResponseRedirect("/accounts/redirect/")
        if request.user.is_superuser:
            return HttpResponseRedirect("/admin-panel/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        logger.info("Logged in user: " + str(self.request.user))
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'Home'
        context['most_popular_books'] = Book.objects.filter(deleted_at__isnull=True).order_by('-avg_rating',
                                                                                              '-created_at')[:3]
        context['newest_books'] = Book.objects.filter(deleted_at__isnull=True).order_by('-published_date',
                                                                                        '-created_at')[:3]
        context['testimonials'] = MemberTestimonial.objects.filter(
            deleted_at__isnull=True).order_by('-created_at')[:5]
        if self.request.user.is_authenticated:
            member = Member.objects.get(username=self.request.user)
            user_based_recommendation = member.user_based_similar_member.all().filter(
                deleted_at__isnull=True).order_by('-prediction')
            context['user_based_recommendation'] = user_based_recommendation
            item_based_recommendation = member.item_based_similar_member.all().filter(
                deleted_at__isnull=True).order_by('-prediction')
            context['item_based_recommendation'] = item_based_recommendation
        return context


class ContactPage(FrontendMixin, CreateMixin):
    template_name = "frontend/contact.html"
    form_class = ContactForm
    model = Contacts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'Contact Us'
        return context

    def get_success_url(self):
        messages.success(self.request, "Message has been sent successfully!")
        return reverse_lazy("my_app:contact_page")


class BookDetailPage(FrontendMixin, DetailView):
    template_name = "frontend/book_details.html"
    model = Book
    queryset = Book.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        book = kwargs.get('object')
        context['available'] = True if book.number_in_stock > 0 else False
        if self.request.user.is_authenticated:
            context['booked'] = False
            context['booking_choices'] = -1
            try:
                member = Member.objects.get(username=self.request.user)
                obj = Booking.objects.filter(
                    user=member, book=self.get_object())
                if obj.count() > 0:
                    if obj.first().status == 1:
                        context['booking_choices'] = 1
                    elif obj.first().status == 2:
                        context['booking_choices'] = 2
                    else:
                        context['booking_choices'] = 3
                rating, created = Ratings.objects.get_or_create(
                    user=member, book=self.get_object())
                context['ratings'] = rating.ratings
                if context['booked'] == False:
                    user_bookings_count = Booking.objects.filter(
                        deleted_at__isnull=True, status=1, user=member).count()
                    if user_bookings_count > 3:
                        context['limit_exceeded'] = True
                user_based_recommendation = member.user_based_similar_member.all().filter(
                    deleted_at__isnull=True).order_by('-book__avg_rating')[:5]
                context['user_based_recommendation'] = user_based_recommendation
                item_based_recommendation = member.item_based_similar_member.all().filter(
                    deleted_at__isnull=True).order_by('-book__avg_rating')[:5]
                context['item_based_recommendation'] = item_based_recommendation
            except Exception as e:
                logger.error(e)
        return context


class ReserveBookView(TemplateView):
    template_name = "frontend/reserve_book.html"

    def dispatch(self, request, *args, **kwargs):
        self.book = Book.objects.get(pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.book
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            member = Member.objects.get(username=request.user)
            user_bookings_count = Booking.objects.filter(
                deleted_at__isnull=True, status=1, user=member).count()
            if not user_bookings_count > 3:
                booking_obj, created = Booking.objects.get_or_create(
                    user=member, book=self.book)
                if not created:
                    booking_obj.status = 1
                    booking_obj.updated_at = timezone.now()
                    booking_obj.deleted_at = None
                    booking_obj.save()
                self.book.number_in_stock -= 1
                self.book.save()
                return HttpResponseRedirect("/detail/" + str(kwargs.get('pk')))
            else:
                return JsonResponse({"msg": "limit_exceeded"})
        else:
            return HttpResponseRedirect("/accounts/login/?next=/detail/" + str(kwargs.get('pk')))


class TestimonialView(LoginRequiredMixin, FrontendMixin, FormView):
    template_name = "frontend/testimonial.html"
    form_class = TestimonialForm

    def post(self, request, *args, **kwargs):
        testimonial_text = request.POST.get('testimonial_text')
        user = Member.objects.get(username=request.user)
        obj = MemberTestimonial.objects.get_or_create(
            user=user, testimonial_text=testimonial_text)
        messages.add_message(request, messages.INFO,
                             'Testimonial successfully sent!')
        return HttpResponseRedirect("/testimonial/")


class RatingView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            user = Member.objects.get(username=request.POST.get('user'))
            book = Book.objects.get(pk=request.POST.get('book_id'))
            ratings_obj, created = Ratings.objects.get_or_create(
                user=user, book=book)
            logger.info(ratings_obj)
            ratings_obj.ratings = int(request.POST.get('rating'))
            ratings_obj.save()
            book.avg_rating = book.avg_rating + \
                (int(request.POST.get('rating')) - book.avg_rating) / \
                Ratings.objects.filter(
                    deleted_at__isnull=True, book=book).count()
            book.save()
            if book.category not in user.category_interests.all():
                user.category_interests.add(book.category)
                user.save()
            return HttpResponse("ok")
        except Exception as e:
            logger.error(e)
            return HttpResponse("wrong")


class BookGalleryPage(FrontendMixin, ListView):
    template_name = "frontend/gallery.html"
    queryset = Book.objects.filter(
        deleted_at__isnull=True).order_by('-created_at')
    paginate_by = 30


class NotificationsPage(LoginRequiredMixin, FrontendMixin, AllNotificationsList):
    template_name = "frontend/notifications.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = Notification.objects.filter(
            recipient=self.request.user).order_by('-timestamp')
        return queryset


class FrontendBookingList(LoginRequiredMixin, FrontendMixin, ListView):
    template_name = "frontend/bookings.html"

    def dispatch(self, request, *args, **kwargs):
        self.user = Member.objects.get(username=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lent_books'] = Booking.objects.filter(
            deleted_at__isnull=True, user=self.user, status=2).order_by('-created_at')
        return context

    def get_queryset(self):
        queryset = Booking.objects.filter(
            deleted_at__isnull=True, user=self.user, status=1)
        return queryset


class FrontendBookingDetails(LoginRequiredMixin, FrontendMixin, DetailView):
    template_name = "frontend/frontend_booking_detail.html"
    model = Booking
    queryset = Booking.objects.filter(deleted_at__isnull=True)


class AboutPage(FrontendMixin, TemplateView):
    template_name = "frontend/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = "About Us"
        return context


class MarkAllAsRead(View):
    def post(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(recipient=request.user)
        for notification in notifications:
            notification.unread = False
            notification.save()
        return HttpResponse('done')


class MarkAsRead(View):
    def post(self, request, *args, **kwargs):
        notification_id = request.POST.get('notification_id')
        notification = Notification.objects.get(pk=notification_id)
        notification.unread = False
        notification.save()
        return HttpResponse('marked as read')


class NotificationGetter(View):
    def get(self, request, *args, **kwargs):
        existing_notifications_ids = request.GET.getlist('notification_list[]')
        user_id = request.GET.get(
            'user_id')
        if existing_notifications_ids is not None:
            new_notifications = Notification.objects.filter(
                recipient=user_id, unread=True).exclude(id__in=existing_notifications_ids)
        else:
            existing_notifications_ids = list()
            new_notifications = Notification.objects.filter(
                recipient=user_id, unread=True)
        existing_notifications_ids += list(
            new_notifications.values_list('id', flat=True))
        notification_count = Notification.objects.filter(
            recipient=user_id, unread=True).count()
        return JsonResponse({"count": notification_count, "notification_list": existing_notifications_ids})


class InterestHandler(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.POST.get("user_id")
            book_id = request.POST.get("book_id")
            category_id = request.POST.get("category_id")
            book_category = Category.objects.get(pk=category_id)
            member = Member.objects.get(pk=user_id)
            semi_possible_interests_exists = book_category in member.semi_possible_interests.all()
            possible_interests_exists = book_category in member.possible_interests.all()
            category_interests_exists = book_category in member.category_interests.all()
            if not semi_possible_interests_exists and not possible_interests_exists and not category_interests_exists:
                member.semi_possible_interests.add(book_category)
            elif semi_possible_interests_exists and not possible_interests_exists and not category_interests_exists:
                member.semi_possible_interests.remove(book_category)
                member.possible_interests.add(book_category)
            elif not semi_possible_interests_exists and possible_interests_exists and not category_interests_exists:
                member.possible_interests.remove(book_category)
                member.category_interests.add(book_category)
            return HttpResponse("ok")
        except Exception as e:
            logger.error(e)
            return HttpResponse("notok")


class SearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('Q')
        return redirect(reverse('my_app:search_result', kwargs={'search_query': search_query}))


class SearchResult(LoginRequiredMixin, FrontendMixin, ListView):
    template_name = "frontend/search.html"
    paginate_by = 15

    def get_queryset(self):
        searchQuery = self.kwargs.get('search_query')
        queryset = Book.objects.filter(deleted_at__isnull=True).filter(
            Q(title__icontains=searchQuery))
        return queryset
