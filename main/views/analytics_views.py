import json
import requests
from datetime import datetime
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings

def analytics(request):
    try:
        # Fetch analytics data
        analytics_response = requests.get(f'{settings.BACKEND_API_URL}/blood-requests-analytics/2')
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
        else:
            analytics_data = {
                'assigned_requests': 0,
                'completed_requests': 0,
                'current_month_requests': 0,
                'hospital_id': 2,
                'total_requests': 0,
                'transit': 0,
                'waiting_requests': 0
            }

        # Fetch inventory data
        inventory_response = requests.get(f'{settings.BACKEND_API_URL}/daily-report/2')
        if inventory_response.status_code == 200:
            inventory_data = inventory_response.json()
            # Sort inventory by blood group and blood part
            sorted_inventory = sorted(
                inventory_data['total_inventory'],
                key=lambda x: (x['blood_group_name'], x['blood_part_name'])
            )
            # Sort expiring components
            sorted_expiring = sorted(
                inventory_data['expiring_tomorrow'],
                key=lambda x: (x['blood_group_name'], x['blood_part_name'])
            )
        else:
            sorted_inventory = []
            sorted_expiring = []

        context = {
            'analytics': analytics_data,
            'inventory': sorted_inventory,
            'expiring': sorted_expiring
        }

        return render(request, 'main/analytics.html', context)

    except requests.exceptions.RequestException:
        return render(request, 'main/analytics.html', {
            'analytics': {
                'assigned_requests': 0,
                'completed_requests': 0,
                'current_month_requests': 0,
                'hospital_id': 2,
                'total_requests': 0,
                'transit': 0,
                'waiting_requests': 0
            },
            'inventory': [],
            'expiring': []
        })