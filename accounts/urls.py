from django.conf.urls import url, include

from .views import *

app_name = "accounts"

urlpatterns = [
    # URLs frontend
    url(r'', include("accounts.urls_frontend")),

    # Librarian URLs
    url(r'^list-librarian/$', LibrarianList.as_view(), name="list_librarian"),
    url(r'^create-librarian/$', LibrarianCreate.as_view(), name='create_librarian'),
    url(r'^update-librarian/(?P<pk>\d+)/$', LibrarianUpdate.as_view(), name="update_librarian"),
    url(r'^detail-librarian/(?P<pk>\d+)/$', LibrarianDetail.as_view(), name="detail_librarian"),
    url(r'^delete-librarian/(?P<pk>\d+)/$', LibrarianDelete.as_view(), name="delete_librarian"),

    # Member URLs
    url(r'^list-member/$', MemberList.as_view(), name="list_member"),
    url(r'^create-member/$', MemberCreate.as_view(), name='create_member'),
    url(r'^update-member/(?P<pk>\d+)/$', MemberUpdate.as_view(), name="update_member"),
    url(r'^detail-member/(?P<pk>\d+)/$', MemberDetail.as_view(), name="detail_member"),
    url(r'^delete-member/(?P<pk>\d+)/$', MemberDelete.as_view(), name="delete_member"),
]
