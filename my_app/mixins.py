import logging

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.contrib import messages
from django.core import serializers
from django.utils import timezone
from django.views.generic import (
    TemplateView, FormView, UpdateView, ListView, CreateView, DetailView, DeleteView)
from django.contrib.auth import authenticate, login, logout

from braces.views import (
    LoginRequiredMixin, SuperuserRequiredMixin, GroupRequiredMixin)
from notifications.models import Notification

from ipware.ip import get_ip

from .models import *

from accounts.models import User

AUDIT_CHOICES = dict(AUDIT_TYPE_CHOICES)

logger = logging.getLogger(__name__)


def storeAuditTrial(prevObj, changeObj, actionType, request):
    aTrial = AuditTrial()
    aTrial.modelType = changeObj._meta.verbose_name.title()
    aTrial.objectId = changeObj.pk
    aTrial.action = actionType
    aTrial.user = request.user
    aTrial.ip = get_ip(request)

    if prevObj:
        aTrial.fromObj = serializers.serialize("json", [prevObj])
    aTrial.toObj = serializers.serialize("json", [changeObj])
    aTrial.save()


class AuthRequiredMixin(SuperuserRequiredMixin, GroupRequiredMixin):
    login_url = reverse_lazy("my_app:admin_login")
    group_required = ["head_librarian", ]


class LibrarianRequiredMixin(LoginRequiredMixin, GroupRequiredMixin):
    login_url = reverse_lazy("my_app:admin_login")
    group_required = ["librarian", "head_librarian", ]


class MemberRequiredMixin(LoginRequiredMixin, GroupRequiredMixin):
    login_url = reverse_lazy("accounts:user_login")
    group_required = ["member", ]


class CreateMixin(CreateView):
    def form_valid(self, form):
        creator = User.objects.get(username=self.request.user)
        form.instance.created_by = creator
        obj = form.save()

        for k, v in AUDIT_CHOICES.items():
            if v == "CREATE":
                key = k
                storeAuditTrial('', obj, key, self.request)
        return super().form_valid(form)


class UpdateMixin(UpdateView):
    def form_valid(self, form):
        creator = User.objects.get(username=self.request.user)
        form.instance.created_by = creator
        prev_obj = self.get_object()
        obj = form.save()

        for k, v in AUDIT_CHOICES.items():
            if v == "UPDATE":
                key = k
                storeAuditTrial(prev_obj, obj, key, self.request)
        return super().form_valid(form)


class DeleteMixin(UpdateView):
    def form_valid(self, form):
        form.instance.deleted_at = timezone.now()
        obj = form.save()
        for k, v in AUDIT_CHOICES.items():
            if v == 'DELETE':
                key = k
                storeAuditTrial('', obj, key, self.request)
        return super().form_valid(form)


class FrontendMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        main_menu = Menu.objects.filter(
            deleted_at__isnull=True, parent=None).order_by(
            '-updated_at').order_by('position')
        context['menu_root'] = Menu.get_root()
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            notifications = Notification.objects.filter(recipient=self.request.user)
            context['notification_list'] = list(notifications.values_list('id', flat=True))
            context['no_of_notifications'] = len(notifications.filter(unread=True))
        return context
