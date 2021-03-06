from django.urls import path
from .views import register_view
from .forms import LoginForm
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('', LoginView.as_view(template_name = 'login/login.html', authentication_form = LoginForm), name='login'),
    path('register/', register_view, name='register')
]