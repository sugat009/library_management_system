from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView)

from my_app.mixins import (CreateMixin, DeleteMixin,
                           UpdateMixin, AuthRequiredMixin, LibrarianRequiredMixin)

from .forms import *


# Librarian CRUD
class LibrarianList(AuthRequiredMixin, ListView):
    template_name = "administration/accounts/librarian/list_librarian.html"
    model = Librarian
    queryset = Librarian.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'librarian'
        return context


class LibrarianCreate(AuthRequiredMixin, CreateMixin):
    template_name = 'administration/accounts/librarian/create_librarian.html'
    model = Librarian
    form_class = LibrarianForm
    success_url = reverse_lazy('accounts:list_librarian')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'librarian'
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        password = get_random_string(length=12)
        obj.set_password(password)
        obj.save()
        group = Group.objects.get(name="librarian")
        obj.groups.add(group)
        obj.save()
        send_mail("Account has been created!", "Dear " + obj.first_name + ",\n\tYour account has been created!\n\tYour username is: " +
                  obj.username + "\n\tYour password is: " + password, settings.EMAIL_HOST_USER, [obj.email], fail_silently=True)
        return super().form_valid(form)


class LibrarianUpdate(AuthRequiredMixin, UpdateMixin):
    template_name = 'administration/accounts/librarian/create_librarian.html'
    model = Librarian
    form_class = LibrarianForm
    success_url = reverse_lazy('accounts:list_librarian')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'librarian'
        return context


class LibrarianDetail(AuthRequiredMixin, DetailView):
    template_name = "administration/accounts/librarian/detail_librarian.html"
    model = Librarian
    queryset = Librarian.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'librarian'
        return context


class LibrarianDelete(AuthRequiredMixin, DeleteMixin):
    template_name = "administration/accounts/librarian/delete_librarian.html"
    model = Librarian
    form_class = LibrarianDeleteForm
    success_url = reverse_lazy("accounts:list_librarian")


# Member CRUD
class MemberList(LibrarianRequiredMixin, ListView):
    template_name = "administration/accounts/member/list_member.html"
    model = Member
    queryset = Member.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'member'
        return context


class MemberCreate(LibrarianRequiredMixin, CreateMixin):
    template_name = 'administration/accounts/member/create_member.html'
    model = Member
    form_class = MemberForm
    success_url = reverse_lazy('accounts:list_member')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'member'
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        password = get_random_string(length=12)
        obj.set_password(password)
        obj.save()
        group = Group.objects.get(name="member")
        obj.groups.add(group)
        obj.save()
        send_mail("Account has been created!", "Dear " + obj.first_name + ",\n\tYour account has been created!\n\tYour username is: " +
                  obj.username + "\n\tYour password is: " + password, settings.EMAIL_HOST_USER, [obj.email], fail_silently=True)
        return super().form_valid(form)


class MemberUpdate(LibrarianRequiredMixin, UpdateMixin):
    template_name = 'administration/accounts/member/create_member.html'
    model = Member
    form_class = MemberForm
    success_url = reverse_lazy('accounts:list_member')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'member'
        return context


class MemberDetail(LibrarianRequiredMixin, DetailView):
    template_name = "administration/accounts/member/detail_member.html"
    model = Member
    queryset = Member.objects.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'member'
        return context


class MemberDelete(LibrarianRequiredMixin, DeleteMixin):
    template_name = "administration/accounts/member/delete_member.html"
    model = Member
    form_class = MemberDeleteForm
    success_url = reverse_lazy("accounts:list_member")
