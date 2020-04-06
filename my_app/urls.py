from django.conf.urls import url, include

from .views import *

app_name = "my_app"

urlpatterns = [
    url(r'', include("my_app.urls_frontend")),

    url(r'^admin-login/$', AdminLogin.as_view(), name='admin_login'),
    url(r'^admin-logout/$', AdminLogout.as_view(), name='admin_logout'),
    url(r'^admin-panel/$', AdminHomePage.as_view(), name='admin_homepage'),

    # Change password URL
    url(r'^users/(?P<user_id>\d+)/password_change/$',
        PasswordChangeView.as_view(), name='changepassword'),

    # member seciton
    url(r'^register/$', Registration.as_view(), name='registration'),

    # Book URLs
    url(r'^list-book/$', ListBook.as_view(), name="list_book"),
    url(r'^create-book/$', CreateBook.as_view(), name='create_book'),
    url(r'^update-book/(?P<pk>\d+)/$', UpdateBook.as_view(), name="update_book"),
    url(r'^detail-book/(?P<pk>\d+)/$', DetailBook.as_view(), name="detail_book"),
    url(r'^delete-book/(?P<pk>\d+)/$', DeleteBook.as_view(), name="delete_book"),

    # Category URLs
    url(r'^list-category/$', ListCategory.as_view(), name="list_category"),
    url(r'^create-category/$', CreateCategory.as_view(), name='create_category'),
    url(r'^update-category/(?P<pk>\d+)/$', UpdateCategory.as_view(), name="update_category"),
    url(r'^delete-category/(?P<pk>\d+)/$', DeleteCategory.as_view(), name="delete_category"),

    # Publisher URLs
    url(r'^list-publisher/$', ListPublisher.as_view(), name="list_publisher"),
    url(r'^create-publisher/$', CreatePublisher.as_view(), name='create_publisher'),
    url(r'^update-publisher/(?P<pk>\d+)/$', UpdatePublisher.as_view(), name="update_publisher"),
    url(r'^delete-publisher/(?P<pk>\d+)/$', DeletePublisher.as_view(), name="delete_publisher"),

    # Menu URLs
    url(r'^list-menu/$', ListMenu.as_view(), name="list_menu"),
    url(r'^create-menu/$', CreateMenu.as_view(), name="create_menu"),
    url(r'^update-menu/(?P<pk>\d+)/$', UpdateMenu.as_view(), name="update_menu"),
    url(r'^delete-menu/(?P<pk>\d+)/$', DeleteMenu.as_view(), name="delete_menu"),
    url(r'^detail-menu/(?P<pk>\d+)/$', DetailMenu.as_view(), name="detail_menu"),

    # Booking URLs
    url(r'^list-booking/$', ListBooking.as_view(), name="list_booking"),
    url(r'^create-booking/$', CreateBooking.as_view(), name="create_booking"),
    url(r'^update-booking/(?P<pk>\d+)/$', UpdateBooking.as_view(), name="update_booking"),
    url(r'^detail-booking/(?P<pk>\d+)$', DetailBooking.as_view(), name="detail_booking"),
    url(r'^delete-booking/(?P<pk>\d+)/$', DeleteBooking.as_view(), name="delete_booking"),

    # Testimonial URLs
    url(r'^list-testimonial/$', ListTestimonial.as_view(), name="list_testimonial"),
    url(r'^detail-testimonial/(?P<pk>\d+)$', DetailTestimonial.as_view(), name="detail_testimonial"),
    url(r'^delete-testimonial/(?P<pk>\d+)/$', DeleteTestimonial.as_view(), name="delete_testimonial"),

    # Contact URLs
    url(r'^list-contact/$', ListContact.as_view(), name="list_contact"),
    url(r'^detail-contact/(?P<pk>\d+)$', DetailContact.as_view(), name="detail_contact"),
    url(r'^delete-contact/(?P<pk>\d+)/$', DeleteContact.as_view(), name="delete_contact"),

    # AJAX URLs
    url(r'change/booking/$', ChangeBookingStatus.as_view(), name="change_booking"),
    url(r'set/return/date/$', SetReturnDate.as_view(), name="set_return_date"),

    # test URL
    url(r'^test/$', TestView.as_view(), name="test_view"),
]
