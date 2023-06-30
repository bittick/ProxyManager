from django.urls import path
from .views import *
from .user_actions.user_api import *

urlpatterns = [
    path('', test),
    path('reg', RegistrationView.as_view()),
    path('auth', authorization),
    path('free_proxy', get_free_proxy),
    path('test', test_auth),
    path('ver_code', confirm_code),
    # path('recover', start_recover_account),
]

