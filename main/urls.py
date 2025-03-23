from django.urls import  path
from .views import index, about, users, contacts

urlpatterns = [
    path('', index, name='home'),
    path('about/', about, name='about'),
    path('users/', users, name='users'),
    path('contacts/', contacts, name='contacts'),

]