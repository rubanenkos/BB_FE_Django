from django.urls import  path
from .views import index, about, login, users, contacts, register, donors, logout, add_user

urlpatterns = [
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('home/', index, name='home'),
    path('about/', about, name='about'),
    path('users/', users, name='users'),
    path('donors/', donors, name='donors'),
    path('contacts/', contacts, name='contacts'),
    path('logout/', logout, name='logout'),
    path('add_user/', add_user, name='add_user'),

]