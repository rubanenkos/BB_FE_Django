from django.urls import  path
from .views import index, about, login, users, contacts, register, donors

urlpatterns = [
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('home/', index, name='home'),
    path('about/', about, name='about'),
    path('users/', users, name='users'),
    path('donors/', donors, name='donors'),
    path('contacts/', contacts, name='contacts'),

]