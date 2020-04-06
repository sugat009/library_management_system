from django.conf.urls import url

from .views_frontend import *


urlpatterns = [
    url(r'^$', HomePage.as_view(), name="homepage"),
    url(r'^contact-us/$', ContactPage.as_view(), name="contact_page"),
    url(r'^detail/(?P<pk>\d+)/$', BookDetailPage.as_view(),
        name="frontend_book_detail"),
    url(r'^testimonial/$', TestimonialView.as_view(), name="testimonial"),
    url(r'^about-us/$', AboutPage.as_view(), name="about_page"),
    url(r'^gallery/$', BookGalleryPage.as_view(), name="book_gallery"),
    url(r'^notifications/$', NotificationsPage.as_view(),
        name="member_notifications"),
    url(r'^user/booking/list/$', FrontendBookingList.as_view(),
        name="frontend_booking_list"),
    url(r'^user/booking/detail/(?P<pk>\d+)/$',
        FrontendBookingDetails.as_view(), name="frontend_booking_detail"),
    url(r'^search-book/$', SearchView.as_view(), name="search_view"),
    url(r'^search/result/(?P<search_query>.*)/$', SearchResult.as_view(), name="search_result"),

    # AJAX urls
    url(r'^reserve/book/(?P<pk>\d+)/$',
        ReserveBookView.as_view(), name="reserve_book"),
    url(r'^rate/book/$', RatingView.as_view(), name="rate_book"),
    url(r'^markallasread/$', MarkAllAsRead.as_view(), name="mark_all_as_read"),
    url(r'^markasread/$', MarkAsRead.as_view(), name="mark_as_read"),
    url(r'^get/notification/$', NotificationGetter.as_view(),
        name="notification_getter"),
    url(r'^category/interest/handler/$', InterestHandler.as_view(), name="interest_handler"),
]
