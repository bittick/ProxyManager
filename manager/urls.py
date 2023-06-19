from django.urls import path
from .views import *

urlpatterns = [
    path('', test),
    path('reg', RegistrationView.as_view()),
    path('auth', authorization),
    path('free_proxy', get_free_proxy),
    path('test', test_auth)
]

