from django.urls import path
from .views import (
    login, logout, register,
    index, about, contacts,
    blood_requests, add_request, add_request_details, search_request,
    deliveries, create_transport,
    users, user_details, add_user,
    analytics, supply,
    change_password
)

urlpatterns = [
    path('', index, name='home'),  # Root URL goes to home
    path('login/', login, name='login'),  # Separate login URL
    path('about/', about, name='about'),
    path('contacts/', contacts, name='contacts'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('requests/', blood_requests, name='requests'),
    path('add_request/', add_request, name='add_request'),
    path('add_request_details/<int:request_blood_id>/', add_request_details, name='add_request_details'),
    path('search_request/<int:request_blood_id>/', search_request, name='search_request'),
    path('deliveries/', deliveries, name='deliveries'),
    path('create_transport/<int:request_blood_id>/', create_transport, name='create_transport'),
    path('users/', users, name='users'),
    path('user-details/', user_details, name='user_details'),
    path('add_user/', add_user, name='add_user'),
    path('analytics/', analytics, name='analytics'),
    path('supply/', supply, name='supply'),
    path('change-password/', change_password, name='change_password'),
]