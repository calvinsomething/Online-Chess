from django.urls import path
from .views import register_view, Login_View


urlpatterns = [
    path('', Login_View.as_view(), name='login'),
    path('register/', register_view, name='register')
]