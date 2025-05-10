from .auth_views import login, logout, register, change_password
from .base_views import index, about, contacts
from .request_views import blood_requests, add_request, add_request_details, search_request
from .delivery_views import deliveries, create_transport
from .user_views import users, user_details, add_user
from .analytics_views import analytics
from .supply_views import supply
from .donor_views import donors, add_donor

__all__ = [
    'login', 'logout', 'register', 'change_password',
    'index', 'about', 'contacts',
    'blood_requests', 'add_request', 'add_request_details', 'search_request',
    'deliveries', 'create_transport',
    'users', 'user_details', 'add_user',
    'analytics',
    'supply',
    'donors', 'add_donor'
]