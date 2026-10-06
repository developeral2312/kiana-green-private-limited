import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zyphora.settings')
django.setup()

from procurement.models import (
    Material, Vendor, Stock, PurchaseOrder, PurchaseOrderItem, 
    GoodsReceived, KitConfiguration, KitMaterial, RequestForQuotation, VendorQuotation
)

def populate_procurement():
    # 1. Create Vendors
    vendor1, _ = Vendor.objects.get_or_create(
        name="SunPower Suppliers Ltd",
        phone="9988771122",
        email="sales@sunpowersuppliers.com",
        defaults={'address': 'Industrial Area, Delhi', 'gst_number': '07AACCS8823K1Z9'}
    )
    
    vendor2, _ = Vendor.objects.get_or_create(
        name="Luminous Power Infra",
        phone="8877665544",
        email="contact@luminouspower.com",
        defaults={'address': 'Sector 62, Noida', 'gst_number': '09AABCD1234E1Z7'}
    )

    # 2. Create Materials
    panel, _ = Material.objects.get_or_create(
        name="Mono PERC 540W Solar Panel",
        category="panel",
        unit="Nos",
        defaults={'brand': 'Waaree', 'unit_price': Decimal('14500.00'), 'minimum_stock': 50}
    )
    
    inverter, _ = Material.objects.get_or_create(
        name="5kW String Inverter",
        category="inverter",
        unit="Nos",
        defaults={'brand': 'Growatt', 'unit_price': Decimal('45000.00'), 'minimum_stock': 10}
    )
    
    cable, _ = Material.objects.get_or_create(
        name="4 sqmm DC Cable (Red/Black)",
        category="cable",
        unit="Meters",
        defaults={'brand': 'Polycab', 'unit_price': Decimal('55.00'), 'minimum_stock': 500}
    )

    structure, _ = Material.objects.get_or_create(
        name="Galvanized Iron (GI) Structure for 5kW",
        category="structure",
        unit="Kit",
        defaults={'brand': 'Generic', 'unit_price': Decimal('12000.00'), 'minimum_stock': 5}
    )

    print("Created Vendors and Materials")

    # 3. Create a Kit Configuration
    kit, _ = KitConfiguration.objects.get_or_create(
        name="Standard 5kW On-Grid Kit",
        system_size_kw=5.0,
        defaults={'description': 'Complete package for residential 5kW setup', 'version': '1.0'}
    )
    
    # Add materials to kit
    KitMaterial.objects.get_or_create(kit=kit, material=panel, defaults={'quantity': 10}) # 10 * 540W ~ 5.4kW
    KitMaterial.objects.get_or_create(kit=kit, material=inverter, defaults={'quantity': 1})
    KitMaterial.objects.get_or_create(kit=kit, material=cable, defaults={'quantity': 100})
    KitMaterial.objects.get_or_create(kit=kit, material=structure, defaults={'quantity': 1})
    
    print("Created 5kW Kit Configuration")

    # 4. Create an RFQ (Request for Quotation)
    rfq, _ = RequestForQuotation.objects.get_or_create(
        title="Urgent requirement for 540W Panels (100 Nos)",
        material=panel,
        quantity_required=100,
        deadline=date.today() + timedelta(days=7),
        defaults={'status': 'published'}
    )
    
    # 5. Create Vendor Quotations against the RFQ
    VendorQuotation.objects.get_or_create(
        rfq=rfq,
        vendor=vendor1,
        defaults={'quoted_price_per_unit': Decimal('14200.00'), 'lead_time_days': 5, 'is_selected': True}
    )
    VendorQuotation.objects.get_or_create(
        rfq=rfq,
        vendor=vendor2,
        defaults={'quoted_price_per_unit': Decimal('14600.00'), 'lead_time_days': 2, 'is_selected': False}
    )
    
    print("Created RFQ and Vendor Quotations (Intelligence)")

    # 6. Create a Purchase Order
    po, _ = PurchaseOrder.objects.get_or_create(
        vendor=vendor1,
        order_date=date.today() - timedelta(days=2),
        expected_delivery=date.today() + timedelta(days=3),
        defaults={'status': 'ordered'}
    )
    
    PurchaseOrderItem.objects.get_or_create(
        purchase_order=po,
        material=panel,
        quantity=50,
        unit_price=Decimal('14200.00')
    )
    PurchaseOrderItem.objects.get_or_create(
        purchase_order=po,
        material=inverter,
        quantity=5,
        unit_price=Decimal('43000.00')
    )
    
    # Calculate PO Total
    po.update_total()

    print("Created Purchase Order")

    # 7. Set some basic stock logic via GoodsReceived to trigger stock update
    # We will create another completed PO to simulate stock arrival
    po2, _ = PurchaseOrder.objects.get_or_create(
        vendor=vendor2,
        order_date=date.today() - timedelta(days=10),
        expected_delivery=date.today() - timedelta(days=2),
        defaults={'status': 'received'}
    )
    PurchaseOrderItem.objects.get_or_create(
        purchase_order=po2,
        material=cable,
        quantity=1000,
        unit_price=Decimal('50.00')
    )
    po2.update_total()
    
    GoodsReceived.objects.get_or_create(
        purchase_order=po2,
        received_date=date.today() - timedelta(days=2),
        defaults={'notes': 'All cables received in good condition'}
    )

    print("Procurement module populated successfully!")

if __name__ == "__main__":
    populate_procurement()
