from django.urls import path
from .views import Register_View, Login_View
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', Login_View.as_view(), name='login'),
    path('register/', Register_View.as_view(), name='register'),
    path('logout/', LogoutView.as_view, name='logout')
]