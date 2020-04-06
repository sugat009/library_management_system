from django.conf.urls import url

from .views_frontend import *

urlpatterns = [
    # login logout related
    url(r'^accounts/signup/$', MemberSignupView.as_view(), name="member_signup"),
    url(r'^accounts/login/$', MemberLoginView.as_view(), name='member_login'),
    url(r'^accounts/logout/$', MemberLogout.as_view(), name='member_logout'),
    # # url(r'^account-password-change/$',MemberPasswordChange.as_view(),name="password_change"),
    url(r'^accounts/redirect/$', MemberRedirectView.as_view(), name="account_redirect"),
    url(r'^accounts/password/change/$', ChangePassword.as_view(), name='password_change'),
    # url(r'^accounts/activate/$', ActivateView.as_view(), name="activate"),
    url(r'^account-activation-sent/(?P<params>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        AccountActivationSentView.as_view(), name="account_activation_sent"),
    url(r'^activation-invalid/$', ActivationInvalidView.as_view(), name="activation_invalid"),
    url(r'^password/changed/forgot/$', ForgotPasswordFormView.as_view(), name='forgot_password'),
    url(r'^resetpassword/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ResetPassword.as_view(), name='reset_password'),

    # profile url
    url(r'^profile/$', ProfileView.as_view(), name="profile"),
    url(r'^history/$', HistoryView.as_view(), name="history"),

    # AJAX URLs
    url(r'^change/profile/pic/$', ChangeProfilePicView.as_view(), name="change_pp"),
    url(r'^create-profession/$', CreateProfessionView.as_view(), name="create_profession"),
]
