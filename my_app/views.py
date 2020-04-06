import logging
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView

from notifications.models import Notification
from notifications.signals import notify

from accounts.forms import MemberForm
from accounts.models import Member
from .forms import *
from .mixins import *

logger = logging.getLogger(__name__)


'''Admin Section'''


class AdminHomePage(LibrarianRequiredMixin, TemplateView):
    template_name = 'administration/library/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'homepage'
        return context


class AdminLogin(TemplateView):
    template_name = 'administration/library/account/login.html'

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            form = LoginForm()
            print(user)
            print('form valid')
            if user is not None:
                if user.is_active:
                    print('user is active')
                    login(request, user)
                    return HttpResponseRedirect('/admin-panel/')
            else:
                print('else')
                # raise forms.ValidationError("Invalid Username or  Password")
                return HttpResponseRedirect('/admin-login')

    def get_context_data(self):
        context = super(AdminLogin, self).get_context_data()
        form = LoginForm()
        context['form'] = form
        return context


class AdminLogout(LibrarianRequiredMixin, TemplateView):
    template_name = 'administration/library/account/logout.html'

    def post(self, request):
        logout(request)
        return HttpResponseRedirect('/admin-login/')


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = "administration/library/account/change_password.html"
    form_class = ChangePasswordForm
    success_url = reverse_lazy('my_app:admin_homepage')
    success_message = "Password Changed Successfully"

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, pk=kwargs['user_id'])
        if not (self.user.groups.first().name == "head_librarian" or self.user.groups.first().name == "librarian"):
            return HttpResponseRedirect("/user-login/")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        logger.info(form.cleaned_data)
        current_password = form.cleaned_data['current_password']
        newpassword = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']
        if not self.request.user.check_password(current_password):
            messages.error(self.request, "Current Password doesn't match")
            return super().form_invalid(form)
        if newpassword != confirm_password:
            messages.error(self.request, "Passwords do not match")
            return super().form_invalid(form)
        self.user.set_password(newpassword)
        self.user.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object'] = self.user
        return context


# Member Section
class Registration(CreateMixin):
    template_name = "administration/frontend/registration.html"
    model = Member
    form_class = MemberForm
    success_url = reverse_lazy('my_app:homepage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'member'
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        obj.save()
        return HttpResponseRedirect('/')


# Book CRUD
class ListBook(LibrarianRequiredMixin, ListView):
    template_name = 'administration/library/books/list_book.html'
    model = Book
    queryset = Book.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'book'
        return context


class CreateBook(LibrarianRequiredMixin, CreateMixin):
    template_name = 'administration/library/books/create_book.html'
    model = Book
    form_class = BookForm
    success_url = reverse_lazy('my_app:list_book')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'book'
        return context


class UpdateBook(LibrarianRequiredMixin, UpdateMixin):
    template_name = 'administration/library/books/create_book.html'
    model = Book
    form_class = BookForm
    success_url = reverse_lazy('my_app:list_book')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'book'
        return context


class DeleteBook(LibrarianRequiredMixin, DeleteMixin):
    template_name = 'administration/library/books/delete_book.html'
    model = Book
    form_class = BookDeleteForm
    success_url = reverse_lazy('my_app:list_book')


class DetailBook(LibrarianRequiredMixin, DetailView):
    template_name = 'administration/library/books/detail_book.html'
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'book'
        return context


# Category CRUD
class ListCategory(LibrarianRequiredMixin, ListView):
    template_name = 'administration/library/category/list_category.html'
    model = Category
    queryset = Category.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'category'
        return context


class CreateCategory(LibrarianRequiredMixin, CreateMixin):
    template_name = 'administration/library/category/create_category.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('my_app:list_category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'category'
        return context


class UpdateCategory(LibrarianRequiredMixin, UpdateMixin):
    template_name = 'administration/library/category/create_category.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('my_app:list_category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'category'
        return context


class DeleteCategory(LibrarianRequiredMixin, DeleteMixin):
    template_name = 'administration/library/category/delete_category.html'
    model = Category
    form_class = CategoryDeleteForm
    success_url = reverse_lazy('my_app:list_category')


# Publisher CRUD
class ListPublisher(LibrarianRequiredMixin, ListView):
    template_name = 'administration/library/publisher/list_publisher.html'
    model = Publisher
    queryset = Publisher.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'publisher'
        return context


class CreatePublisher(LibrarianRequiredMixin, CreateMixin):
    template_name = 'administration/library/publisher/create_publisher.html'
    model = Publisher
    form_class = PublisherForm
    success_url = reverse_lazy('my_app:list_publisher')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'publisher'
        return context


class UpdatePublisher(LibrarianRequiredMixin, UpdateMixin):
    template_name = 'administration/library/publisher/create_publisher.html'
    model = Publisher
    form_class = PublisherForm
    success_url = reverse_lazy('my_app:list_publisher')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'publisher'
        return context


class DeletePublisher(LibrarianRequiredMixin, DeleteMixin):
    template_name = 'administration/library/publisher/delete_publisher.html'
    model = Publisher
    form_class = PublisherDeleteForm
    success_url = reverse_lazy('my_app:list_publisher')


# Menu CRUD
class ListMenu(LibrarianRequiredMixin, ListView):
    template_name = 'administration/library/menu/list_menu.html'
    model = Menu
    queryset = Menu.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'menu'
        return context


class CreateMenu(LibrarianRequiredMixin, CreateMixin):
    template_name = 'administration/library/menu/create_menu.html'
    model = Menu
    form_class = MenuForm
    success_url = reverse_lazy('my_app:list_menu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'menu'
        return context


class UpdateMenu(LibrarianRequiredMixin, UpdateMixin):
    template_name = 'administration/library/menu/create_menu.html'
    model = Menu
    form_class = MenuForm
    success_url = reverse_lazy('my_app:list_menu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'menu'
        return context


class DetailMenu(LibrarianRequiredMixin, DetailView):
    template_name = "administration/library/menu/detail_menu.html"
    model = Menu
    queryset = Menu.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'menu'
        return context


class DeleteMenu(LibrarianRequiredMixin, DeleteMixin):
    template_name = 'administration/library/menu/delete_menu.html'
    model = Menu
    form_class = MenuDeleteForm
    success_url = reverse_lazy('my_app:list_menu')


# Booking CRUD
class ListBooking(LibrarianRequiredMixin, ListView):
    template_name = 'administration/library/bookings/list_booking.html'
    model = Booking
    queryset = Booking.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'booking'
        return context


class CreateBooking(LibrarianRequiredMixin, CreateMixin):
    template_name = "administration/library/bookings/create_booking.html"
    model = Booking
    form_class = BookingForm
    success_url = reverse_lazy("my_app:list_booking")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'booking'
        return context


class UpdateBooking(LibrarianRequiredMixin, UpdateMixin):
    template_name = 'administration/library/bookings/create_booking.html'
    model = Booking
    form_class = BookingForm
    success_url = reverse_lazy('my_app:list_booking')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'booking'
        return context


class DetailBooking(LibrarianRequiredMixin, DetailView):
    template_name = 'administration/library/bookings/detail_booking.html'
    model = Booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'booking'
        return context


class DeleteBooking(LibrarianRequiredMixin, DeleteMixin):
    template_name = 'administration/library/bookings/delete_booking.html'
    model = Booking
    form_class = BookingDeleteForm
    success_url = reverse_lazy('my_app:list_booking')


# CRUD Testimonial
class ListTestimonial(LibrarianRequiredMixin, ListView):
    template_name = 'administration/library/testimonial/list_testimonial.html'
    model = MemberTestimonial
    queryset = MemberTestimonial.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'testimonial'
        return context


class DetailTestimonial(LibrarianRequiredMixin, DetailView):
    template_name = 'administration/library/testimonial/detail_testimonial.html'
    model = MemberTestimonial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'testimonial'
        return context


class DeleteTestimonial(LibrarianRequiredMixin, DeleteMixin):
    template_name = 'administration/library/testimonial/delete_testimonial.html'
    model = MemberTestimonial
    form_class = TestimonialDeleteForm
    success_url = reverse_lazy('my_app:list_testimonial')


# CRUD Contact
class ListContact(LibrarianRequiredMixin, ListView):
    template_name = 'administration/library/messages/list_message.html'
    model = Contacts
    queryset = Contacts.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contact'
        return context


class DetailContact(LibrarianRequiredMixin, DetailView):
    template_name = 'administration/library/messages/detail_message.html'
    model = Contacts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contact'
        return context


class DeleteContact(LibrarianRequiredMixin, DeleteMixin):
    template_name = 'administration/library/messages/delete_message.html'
    model = Contacts
    form_class = ContactDeleteForm
    success_url = reverse_lazy('my_app:list_contact')


# AJAX view to change booking status of book
class ChangeBookingStatus(LibrarianRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            new_booking_status = request.POST.get('booking_status')
            booking_id = request.POST.get('booking_id')
            obj = Booking.objects.get(pk=booking_id)
            if not obj.status == new_booking_status:
                obj.status = new_booking_status
                obj.save()
                if int(new_booking_status) == 2:
                    notify.send(obj, recipient=obj.user, action_object=obj.book, verb="You have lent " + str(
                        obj.book) + " from the library.", description="book lent")
                elif int(new_booking_status) == 3:
                    obj.book.number_in_stock += 1
                    obj.book.save()
                    notify.send(obj, recipient=obj.user, action_object=obj.book,
                                verb="You have returned " + str(obj.book) + " to the library.", description="book lent")
            return HttpResponse("ok")
        except Exception as e:
            logger.error(e)
            return HttpResponse("not")


# AJAX set return date of book
class SetReturnDate(LibrarianRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        date = request.POST.get('date')
        booking_id = request.POST.get('booking_id')
        try:
            obj = Booking.objects.get(pk=booking_id)
            parsed_date = datetime.strptime(
                date, '%m/%d/%Y').strftime('%Y-%m-%d')
            obj.return_date = parsed_date
            obj.save()
            return JsonResponse({"msg": "ok", "date": obj.return_date})
        except Exception as e:
            logger.error(e)
            return JsonResponse({"msg": "not"})


class TestView(SuperuserRequiredMixin, TemplateView):
    template_name = "administration/library/test.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user =  Member.objects.get(username='tester2')
        context["user_based"] = user.user_based_similar_member.all()
        print(context['user_based'])
        return context
    
