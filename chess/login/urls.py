from django.urls import path
from .views import Register_View, Login_View


urlpatterns = [
    path('', Login_View.as_view(), name='login'),
    path('register/', Register_View.as_view(), name='register')
]