from django.urls import  path
from .views import index, about, login, users, contacts, register

urlpatterns = [
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('home/', index, name='home'),
    path('about/', about, name='about'),
    path('users/', users, name='users'),
    path('contacts/', contacts, name='contacts'),

]