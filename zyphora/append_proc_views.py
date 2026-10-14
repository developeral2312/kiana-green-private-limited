with open('procurement/views.py', 'a', encoding='utf-8') as f:
    f.write('''

# ===============================
# FEATURE 13: PROCUREMENT INTELLIGENCE (RFQ)
# ===============================

@login_required(login_url='/users/login')
def rfq_list(request):
    rfqs = RequestForQuotation.objects.all().order_by('-created_at')
    return render(request, 'dashboard/procurement/rfq_list.html', {'rfqs': rfqs})

@login_required(login_url='/users/login')
def rfq_detail(request, rfq_id):
    rfq = get_object_or_404(RequestForQuotation, id=rfq_id)
    quotations = rfq.quotations.all().order_by('total_amount')
    
    if quotations.exists() and rfq.status == 'evaluating':
        # Auto-detect L1
        l1_quote = quotations.first()
        if not l1_quote.is_l1:
            VendorQuotation.objects.filter(rfq=rfq).update(is_l1=False)
            l1_quote.is_l1 = True
            l1_quote.save()

    context = {
        'rfq': rfq,
        'quotations': quotations
    }
    return render(request, 'dashboard/procurement/rfq_detail.html', context)

@login_required(login_url='/users/login')
def award_rfq(request, rfq_id, quote_id):
    rfq = get_object_or_404(RequestForQuotation, id=rfq_id)
    quote = get_object_or_404(VendorQuotation, id=quote_id, rfq=rfq)
    
    # Update statuses
    rfq.status = 'closed'
    rfq.save()
    
    VendorQuotation.objects.filter(rfq=rfq).update(status='rejected')
    quote.status = 'accepted'
    quote.save()
    
    # Auto-generate PO
    po = PurchaseOrder.objects.create(
        vendor=quote.vendor,
        order_date=timezone.now().date(),
        status='pending',
        total_amount=quote.total_amount
    )
    for q_item in quote.items.all():
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            material=q_item.rfq_item.material,
            quantity=q_item.quantity,
            unit_price=q_item.unit_price
        )
    
    messages.success(request, f"RFQ Awarded to {quote.vendor.name}. Purchase Order PO-{po.id} generated.")
    return redirect('po_detail', pid=po.id)
''')
print("Appended views")
