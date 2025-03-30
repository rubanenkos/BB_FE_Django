from .menu_config import MENU_ITEMS

def menu_items(request):
    user_role = request.session.get('user', {}).get('role_id')
    return {
        'menu_items': MENU_ITEMS.get(user_role, [])
    }