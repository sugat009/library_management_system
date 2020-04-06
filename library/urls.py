from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

import notifications.urls

from accounts.views_frontend import AccountActivationView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include("accounts.urls")),
    url(r'', include("my_app.urls")),
    url(r'', include("my_app.urls_frontend")),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        AccountActivationView.as_view(), name="activate"),
    url(r'^inbox/notifications/', include(notifications.urls, namespace='notifications')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
