import logging
import re
import json

from django.utils.html import strip_tags
from django.views.generic import FormView, TemplateView, DetailView, ListView
from django.views import View
from django.shortcuts import redirect, HttpResponseRedirect, HttpResponse, render
from django.http import JsonResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate, logout
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.models import Group

from braces.views import LoginRequiredMixin

from .forms import (FirstLoginForm, RegistrationForm,
                    MemberLoginForm, ForgotPasswordForm, NewPassword)
from .models import Member, User

from my_app.tokens import account_activation_token
from my_app.forms import ChangePasswordForm, ProfessionForm
from my_app.mixins import FrontendMixin
from my_app.models import Booking
from my_app.recommender import handle_new_users, insert_update_jaccard_similarity_table


logger = logging.getLogger(__name__)


class MemberSignupView(FrontendMixin, FormView):
    template_name = "frontend/signup.html"
    form_class = RegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'signup'
        return context

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if Member.objects.filter(email=request.POST.get("email")).count() > 0:
            messages.error(self.request, "User with that email already exists!")
            return HttpResponseRedirect("/accounts/signup/")
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = request.META['HTTP_HOST']
            subject = 'Activate Your Account'
            message = render_to_string('frontend/account_activation_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail("Activate Your Account", message,
                      settings.EMAIL_HOST_USER, [user.email])
            return HttpResponseRedirect("/account-activation-sent/" + str(user.email))
        else:
            form_fields = json.loads(form.errors.as_json()).keys()
            for field in form_fields:
                messages.error(self.request, json.loads(form.errors.as_json())[field][0]['message'])
            return HttpResponseRedirect("/accounts/signup/")


class MemberLoginView(FrontendMixin, FormView):
    template_name = "frontend/login.html"
    form_class = MemberLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'login'
        return context

    def post(self, request, *args, **kwargs):
        form = MemberLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if username == None or password == None:
                return JsonResponse({"msg": "empty"})
            if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", username):
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except Exception as e:
                    logger.error(e)
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    if not user.is_superuser:
                        login(request, user)
                        if len(request.META['HTTP_REFERER'].split("=")) > 1:
                            url_list = request.META['HTTP_REFERER'].split("=")
                            return JsonResponse({"msg": "valid", "url_extra": url_list[1]})
                        else:
                            return JsonResponse({"msg": "valid"})
            else:
                return JsonResponse({"msg": "invalid"})
        else:
            return JsonResponse({"msg": "empty"})


class MemberRedirectView(LoginRequiredMixin, FrontendMixin, FormView):
    template_name = "frontend/redirect.html"
    model = Member
    form_class = FirstLoginForm
    success_message = "Profile information has been added successfully"
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        member = Member.objects.get(username=request.user)
        if member.first_name and member.last_name:
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        logger.debug(form.cleaned_data)
        user = Member.objects.get(username=self.request.user)
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        if form.cleaned_data['photo']:
            photo = form.cleaned_data['photo']
            user.photo = photo
        if form.cleaned_data['phone_number']:
            phone_number = form.cleaned_data['phone_number']
            user.phone_number = str(phone_number)
        address = form.cleaned_data['address']
        category_interests = form.cleaned_data.get('category_interests', None)
        profession = form.cleaned_data.get('profession', None)
        user.first_name = first_name
        user.last_name = last_name
        user.address = address
        user.category_interests = category_interests
        user.profession = profession
        user.save()
        try:
            insert_update_jaccard_similarity_table(user)
            handle_new_users(user, 'itembased')
            # handle_new_users(user, 'userbased')
        except Exception as e:
            logger.error(e)
            logger.error("error while writing to handle new user")
        return super().form_valid(form)


class ChangePassword(LoginRequiredMixin, FrontendMixin, FormView):
    form_class = ChangePasswordForm
    template_name = 'frontend/changepassword.html'
    success_url = '/accounts/login/'

    def form_valid(self, form):
        current_password = form.cleaned_data.get('current_password')
        password = form.cleaned_data.get('password')
        confirm_password = form.cleaned_data.get('confirm_password')
        if not self.request.user.check_password(current_password):
            messages.error(self.request, "Current Password doesn't match")
            return super().form_invalid(form)
        if password != confirm_password:
            messages.error(self.request, "Passwords do not match")
            return super().form_invalid(form)
        password = form.cleaned_data.get('password')
        user = self.request.user
        user.set_password(password)
        user.save()
        messages.success(self.request, "Please log in with new password")
        return super().form_valid(form)


class AccountActivationSentView(TemplateView):
    template_name = "frontend/account_activation_sent.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['email'] = kwargs.get("params", None)
        return context


class AccountActivationView(TemplateView):
    template_name = "frontend/account_activation_email.html"

    def get(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64')))
            user = Member.objects.get(pk=uid)
        except Exception as e:
            user = None
            logger.error(e)
            return HttpResponseRedirect("/activation-invalid/")
        try:
            logger.debug(account_activation_token.check_token(user, kwargs.get('token', None)))
            if user is not None and account_activation_token.check_token(user, kwargs.get('token', None)):
                user.is_active = True
                user.email_confirmed = True
                my_group = Group.objects.get(name="member")
                user.groups.add(my_group)
                user.save()
                login(request, user,
                      backend=settings.AUTHENTICATION_BACKENDS[0])
                return HttpResponseRedirect("/accounts/redirect/")
            else:
                if user is not None:
                    user.remove()
                return HttpResponseRedirect("/activation-invalid/")
        except Exception as e:
            logger.error(e)
            return HttpResponseRedirect("/activation-invalid/")


class ActivationInvalidView(FrontendMixin, TemplateView):
    template_name = "frontend/activation_invalid.html"


class MemberLogout(LoginRequiredMixin, TemplateView):
    template_name = "frontend/logout.html"

    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect("/")


class ForgotPasswordFormView(View):

    # def get(self, request, *args, **kwargs):
    #     form = ForgotPasswordForm()
    #
    #     return render(request, 'news/user/login_user.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            to_email = form.cleaned_data['email']
            user = User.objects.get(email=to_email)
            primarykey = user.id
            current_site = request.META['HTTP_HOST']
            subject = 'Passwor Reset !!'
            message = render_to_string('frontend/newpasswordlink.html', {
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(primarykey)),
                'token': account_activation_token.make_token(user),
            })

            send_mail(subject, message, settings.EMAIL_HOST_USER, [to_email])
        return render(request, 'frontend/sendmail.html')


class ResetPassword(View):
    def get(self, request, uidb64, token):
        form = NewPassword()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            return render(request, 'frontend/newpasswordcreate.html', {'form': form})
        else:
            return render(request, 'frontend/activation_invalid.html')

    def post(self, request, uidb64, token):

        form = NewPassword(request.POST)
        if form.is_valid():
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            pass1 = form.cleaned_data['password1']
            pass2 = form.cleaned_data['password2']
            if pass1 != pass2:
                return render(request, 'frontend/passwordnotmatch.html')
            else:
                user.set_password(pass1)
                user.save()
                # return HttpResponse('complete password verification!!')
                return render(request, 'frontend/success.html')


class ProfileView(LoginRequiredMixin, FrontendMixin, TemplateView):
    template_name = "frontend/profile.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = Member.objects.get(username=self.request.user)
        context['url_name'] = 'Profile'
        context['user'] = user
        return context


class HistoryView(LoginRequiredMixin, FrontendMixin, ListView):
    template_name = "frontend/history.html"
    paginate_by = 12

    def get_queryset(self):
        user = Member.objects.get(username=self.request.user)
        bookings = Booking.objects.filter(deleted_at__isnull=True, user=user).order_by('-created_at')
        return bookings


class ChangeProfilePicView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            member = Member.objects.get(username=request.user)
            member.photo = request.FILES.get('profile_pic')
            member.save()
            return JsonResponse({"msg": "ok", "new_pic_url": member.photo.url})
        except Exception as e:
            logger.error(e)
            return JsonResponse({"msg": "error"})


class CreateProfessionView(LoginRequiredMixin, FrontendMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            form = ProfessionForm(request.POST)
            if form.is_valid():
                obj = form.save()
                return JsonResponse({"id": obj.id}, status=200)
            else:
                pass
        except Exception as e:
            logger.error(e)
            return JsonResponse({"msg": "error"}, status=500)