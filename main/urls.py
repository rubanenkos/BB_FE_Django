from django.urls import  path

from .views import (
    add_supply, add_supply_details, add_user, add_donor,
    index, about, login, logout,
    users, contacts, register, donors,
    supply, process_supply, blood_requests,
    add_request, add_request_details, search_request,
    approve_request, deliveries, create_transport, analytics,
    user_details, change_password
)
urlpatterns = [
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('home/', index, name='home'),
    path('about/', about, name='about'),
    path('users/', users, name='users'),
    path('donors/', donors, name='donors'),
    path('contacts/', contacts, name='contacts'),
    path('requests/', blood_requests, name='requests'),
    path('deliveries/', deliveries, name='deliveries'),
    path('logout/', logout, name='logout'),
    path('add_user/', add_user, name='add_user'),
    path('add_donor/', add_donor, name='add_donor'),
    path('supply/', supply, name='supply'),
    path('add_supply/', add_supply, name='add_supply'),
    path('add_supply_details/<int:supply_id>/', add_supply_details, name='add_supply_details'),
    path('process_supply/<int:supply_id>/', process_supply, name='process_supply'),
    path('add_request/', add_request, name='add_request'),
    path('add_request_details/<int:request_blood_id>/', add_request_details, name='add_request_details'),
    path('search_request/<int:request_blood_id>/', search_request, name='search_request'),
    path('approve_request/<int:request_blood_id>/', approve_request, name='approve_request'),
    path('create_transport/<int:request_blood_id>/', create_transport, name='create_transport'),
    path('analytics/', analytics, name='analytics'),
    path('user-details/', user_details, name='user_details'),
    path('change-password/', change_password, name='change_password'),

]