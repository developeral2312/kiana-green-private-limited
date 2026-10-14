from django.urls import path
from .views import *

urlpatterns = [
    path('', partner_list, name='partner_list'),
    path('leads/', all_partner_leads, name='all_partner_leads'),
    path('leads/add/', add_global_lead, name='add_global_lead'),
    path('leads/<int:lead_id>/update/', update_partner_lead, name='update_partner_lead'),
    path('leads/<int:lead_id>/delete/', delete_partner_lead, name='delete_partner_lead'),
    path('stock/', all_dealer_stocks, name='all_dealer_stocks'),
    path('add/', add_partner, name='add_partner'),
    path('<int:pk>/', partner_detail, name='partner_detail'),
    path('<int:pk>/add-lead/', add_partner_lead, name='add_partner_lead'),
    path('<int:pk>/update-stock/', update_partner_stock, name='update_partner_stock'),
    
    # PORTAL
    path('portal/', partner_portal_dashboard, name='partner_portal_dashboard'),
    path('portal/add-lead/', partner_portal_add_lead, name='partner_portal_add_lead'),
]
