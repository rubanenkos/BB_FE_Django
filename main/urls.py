from django.urls import  path

from .views import (
    add_supply, add_supply_details, add_user, add_donor,
    index, about, login, logout,
    users, contacts, register, donors,
    supply
)
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
    path('add_donor/', add_donor, name='add_donor'),
    path('supply/', supply, name='supply'),
    path('add_supply/', add_supply, name='add_supply'),
    path('add_supply_details/<int:supply_id>/', add_supply_details, name='add_supply_details'),
    # path('get_supply_details/<int:supply_id>/', get_supply_details, name='get_supply_details'),

]