from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.forms import modelformset_factory
from django.core.paginator import Paginator
from django.http import JsonResponse
from collections import defaultdict

from .models import *
from .forms import *

from users.utils import create_notification




@login_required(login_url='/users/login')
def material_list(request):
    query = request.GET.get("q")
    category = request.GET.get("category")

    materials = Material.objects.select_related("stock")

    # Search
    if query:
        materials = materials.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query)
        )

    # Category filter
    if category:
        materials = materials.filter(category__iexact=category)

    distinct_categories = Material.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct().order_by('category')
    category_choices = [(c, c.replace('_', ' ').title()) for c in distinct_categories]

    context = {
        "materials": materials,
        "category_choices": category_choices,
        "category": category,
    }

    return render(request, "dashboard/material_list.html", context)


def edit_material(request, mid):
    material = Material.objects.get(id=mid)

    if request.method == "POST":
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return redirect(material_list)  
    else:
        form = MaterialForm(instance=material)
    
    return render(request, "dashboard/edit_material.html", {"form": form, "material": material})

def delete_material(request, mid):
    material = Material.objects.get(id=mid)
    
    if request.method == "POST":
        material.delete()
        
    return redirect('material_list')

@login_required(login_url='/users/login')
def add_material(request):

    form = MaterialForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Material created successfully")
        return redirect("material_list")

    return render(request, "dashboard/add_material.html", {"form": form})



@login_required(login_url='/users/login')
def vendor_list(request):

    query = request.GET.get("q")

    vendors = Vendor.objects.all()

    if query:
        vendors = vendors.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, "dashboard/vendor_list.html", {"vendors": vendors})

def view_vendor(request, vid):

    vendor = get_object_or_404(Vendor, id=vid)

    context = {
        "vendor": vendor
    }

    return render(request, "dashboard/view_vendor.html", context)

@login_required(login_url='/users/login')
def add_vendor(request):

    form = VendorForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Vendor added successfully")
        return redirect("vendor_list")

    return render(request, "dashboard/add_vendor.html", {"form": form})

def edit_vendor(request, vid):
    vendor = get_object_or_404(Vendor, id=vid)
    
    if request.method == "POST":
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect(vendor_list) 
    else:
        form = VendorForm(instance=vendor)
    
    return render(request, "dashboard/edit_vendor.html", {"form": form, "vendor": vendor})


def delete_vendor(request, vid):
    vendor = get_object_or_404(Vendor, id=vid)
    
    if request.method == "POST":
        vendor.delete()
    
    return redirect(vendor_list)


@login_required(login_url='/users/login')
def purchase_order_list(request):

    query = request.GET.get('q', '')
    today = timezone.localdate()

    if query:
        purchase_orders = PurchaseOrder.objects.filter(
            Q(id__icontains=query) | Q(vendor__name__icontains=query)
        ).order_by('-order_date')
    else:
        purchase_orders = PurchaseOrder.objects.all().order_by('-order_date')

    # Add overdue days dynamically
    for po in purchase_orders:
        if po.expected_delivery and po.expected_delivery < today and po.status not in ['received', 'cancelled']:
            po.overdue_days = (today - po.expected_delivery).days
        else:
            po.overdue_days = 0

    context = {
        "purchase_orders": purchase_orders,
        "today": today
    }
    return render(request, "dashboard/purchase_order_list.html", context)


@login_required(login_url='/users/login/')
def purchase_order_detail(request,oid):
    po = get_object_or_404(PurchaseOrder, id=oid)
    items = po.items.all()
    today = timezone.localdate()

    context = {
        "po": po,
        "items": items,
        "today": today
    }
    return render(request, 'dashboard/purchase_order_detail.html', context)


@login_required(login_url='/users/login/')
def receive_purchase_order(request, oid):
    po = get_object_or_404(PurchaseOrder, id=oid)

    if po.status not in ['received', 'cancelled']:
        po.status = 'received'
        po.save()

    return redirect(purchase_order_list)


@login_required(login_url='/users/login/')
def cancel_purchase_order(request,oid):
    po = get_object_or_404(PurchaseOrder, id=oid)

    if po.status not in ['received', 'cancelled']:
        po.status = 'cancelled'
        po.save()

    return redirect('purchase_order_list')


@login_required(login_url='/users/login')
def create_purchase_order(request):

    if request.method == "POST":

        form = PurchaseOrderForm(request.POST)

        if form.is_valid():

            po = form.save(commit=False)
            po.total_amount = 0
            po.save()

            materials = request.POST.getlist("material[]")
            quantities = request.POST.getlist("quantity[]")
            prices = request.POST.getlist("price[]")

            for material, qty, price in zip(materials, quantities, prices):
                if material and qty and price:
                    mat_str = str(material).strip()
                    if mat_str.isdigit():
                        mat_obj = Material.objects.filter(id=int(mat_str)).first()
                    else:
                        mat_obj = Material.objects.filter(name__iexact=mat_str).first()
                        if not mat_obj:
                            mat_obj = Material.objects.create(
                                name=mat_str,
                                unit="Units",
                                minimum_stock=5
                            )
                            Stock.objects.get_or_create(material=mat_obj, defaults={'quantity': 0})

                    if mat_obj:
                        PurchaseOrderItem.objects.create(
                            purchase_order=po,
                            material=mat_obj,
                            quantity=int(qty),
                            unit_price=float(price)
                        )

            # update total
            po.update_total()

            messages.success(request, "Purchase Order created successfully")

            return redirect("purchase_order_list")

    else:
        form = PurchaseOrderForm()

    materials = Material.objects.all()

    context = {
        "form": form,
        "materials": materials
    }

    return render(request, "dashboard/create_purchase_order.html", context)



@login_required(login_url='/users/login')
def goods_received_list(request):

    
    q = request.GET.get("q")

    goods = GoodsReceived.objects.select_related(
        "purchase_order",
        "purchase_order__vendor",
        "received_by"
    ).order_by("-created_at")
    from datetime import date

    today = date.today()
    for g in goods:
        g.days_since_received = (today - g.received_date).days

    if q:
        goods = goods.filter(
            Q(purchase_order__id__icontains=q) |
            Q(purchase_order__vendor__name__icontains=q)
        )


    return render(request, "dashboard/goods_received_list.html", {"goods": goods})




@login_required(login_url='/users/login')
def add_goods_received(request):

    oid = request.GET.get('po')
    initial_data = {}
    if oid:
        initial_data['purchase_order'] = oid

    if request.method == "POST":
        form = GoodsReceivedForm(request.POST)
        if form.is_valid():
            goods = form.save()
            # Update PO status to received
            po = goods.purchase_order
            po.status = 'received'
            po.save()
            return redirect('purchase_order_list')
    else:
        form = GoodsReceivedForm(initial=initial_data)

    return render(request, "dashboard/add_goods_received.html", {"form": form})


@login_required(login_url='/users/login')
def stock_list(request):

    q = request.GET.get("q")

    stocks = Stock.objects.select_related("material").order_by("material__name")

    if q:
        stocks = stocks.filter(
            Q(material__name__icontains=q) |
            Q(material__brand__icontains=q)
        )

    return render(request, "dashboard/stock_list.html", {"stocks": stocks })




@login_required(login_url='/users/login')
def allocation_list(request):
    user = request.user
    q = request.GET.get("q")

    if user.role in ['admin', 'manager', 'director', 'procurement'] or user.is_superuser:
        allocations = MaterialAllocation.objects.all()
    elif user.role == 'subcontractor':
        allocations = MaterialAllocation.objects.filter(project__subcontractor_tasks__subcontractor=user)
    elif user.role == 'engineer':
        allocations = MaterialAllocation.objects.filter(
            Q(project__engineer__user=user) | Q(project__installation_tasks__assigned_to=user)
        )
    elif user.role == 'staff':
        allocations = MaterialAllocation.objects.filter(project__installation_tasks__assigned_to=user)
    else:
        allocations = MaterialAllocation.objects.none()

    allocations = allocations.select_related(
        "project",
        "material",
        "material__stock",
        "allocated_by"
    ).order_by("project__title", "-allocated_date").distinct()

    if q:
        allocations = allocations.filter(
            Q(project__title__icontains=q) |
            Q(material__name__icontains=q)
        )

    # 🔥 GROUP BY PROJECT
    project_allocations = defaultdict(list)

    for a in allocations:
        project_allocations[a.project].append(a)

    context = {
        "project_allocations": dict(project_allocations)
    }

    return render(request, "dashboard/allocation_list.html", context)



@login_required(login_url='/users/login')
def allocate_material(request):
    user = request.user
    if request.method == "POST":
        form = MaterialAllocationForm(request.POST, user=user)

        if form.is_valid():
            allocation = form.save(commit=False)
            material_name = form.cleaned_data.get('material_name', '').strip()
            quantity = form.cleaned_data.get('quantity', 1)

            if not material_name:
                form.add_error('material_name', 'Please write or enter material/hardware name.')
            elif quantity <= 0:
                form.add_error('quantity', 'Quantity must be at least 1.')
            else:
                # Find existing material or dynamically create from manual input
                material = Material.objects.filter(name__iexact=material_name).first()
                if not material:
                    material = Material.objects.create(
                        name=material_name,
                        category='accessory',
                        unit='Units',
                        minimum_stock=0
                    )
                    Stock.objects.get_or_create(material=material, defaults={'quantity': 100})

                allocation.material = material
                allocation.quantity = quantity
                allocation.allocated_by = request.user
                allocation.save()

                # Deduct stock if available
                if hasattr(material, 'stock') and material.stock.quantity > 0:
                    material.stock.quantity = max(0, material.stock.quantity - quantity)
                    material.stock.save()

                messages.success(request, f"Material '{material.name}' ({quantity} {material.unit}) allocated to '{allocation.project.title}' successfully.")
                return redirect('allocation_list')

    else:
        form = MaterialAllocationForm(user=user)

    project_count = form.fields['project'].queryset.count()
    all_materials = Material.objects.select_related('stock').all().order_by('name')

    return render(request, 'dashboard/allocate_material.html', {
        'form': form,
        'project_count': project_count,
        'all_materials': all_materials,
    })


def get_material_stock(request, material_id=None):
    name = request.GET.get('name')
    if name:
        material = Material.objects.filter(name__iexact=name.strip()).first()
    elif material_id:
        material = Material.objects.filter(id=material_id).first()
    else:
        material = None

    if not material:
        return JsonResponse({
            'exists': False,
            'stock': 0,
            'unit': 'Units',
            'name': name or '',
            'category': 'Custom / Site Hardware',
            'is_low_stock': False,
            'min_stock': 0
        })

    stock_qty = material.stock.quantity if hasattr(material, 'stock') else 0
    return JsonResponse({
        'exists': True,
        'stock': stock_qty,
        'unit': material.unit or 'Units',
        'name': material.name,
        'category': material.get_category_display() if material.category else 'General',
        'is_low_stock': material.is_low_stock,
        'min_stock': material.minimum_stock,
    })



def request_material(request):
    MaterialFormSet = modelformset_factory(
        MaterialAllocation,
        form=MaterialAllocationRequestForm,
        extra=1,
        can_delete=True
    )

    if request.method == "POST":
        formset = MaterialFormSet(
            request.POST,
            queryset=MaterialAllocation.objects.none(),
            form_kwargs={'user': request.user}
        )

        if formset.is_valid():
            for form in formset:
                if not form.cleaned_data:
                    continue
                if form.cleaned_data.get('DELETE'):
                    continue

                project = form.cleaned_data.get('project')
                material_name = form.cleaned_data.get('material_name', '').strip()
                quantity = form.cleaned_data.get('quantity', 1)

                if not project or not material_name:
                    continue

                # Match existing warehouse material or create new custom material
                material = Material.objects.filter(name__iexact=material_name).first()
                if not material:
                    material = Material.objects.create(
                        name=material_name,
                        unit='Units',
                        minimum_stock=0
                    )
                    Stock.objects.get_or_create(material=material, defaults={'quantity': 0})

                existing = MaterialAllocation.objects.filter(
                    project=project,
                    material=material,
                    allocated_by=request.user,
                    status='pending'
                ).first()

                if existing:
                    # ✅ Merge duplicate requests
                    existing.quantity += quantity
                    existing.save()
                else:
                    allocation = form.save(commit=False)
                    allocation.material = material
                    allocation.allocated_by = request.user
                    allocation.status = 'pending'
                    allocation.save()

            messages.success(request, "Material request(s) submitted successfully.")
            return redirect('my_requests')

    else:
        formset = MaterialFormSet(
            queryset=MaterialAllocation.objects.none(),
            form_kwargs={'user': request.user}
        )

    all_materials = Material.objects.all().order_by('name')
    return render(request, "dashboard/request_material.html", {
        "formset": formset,
        "all_materials": all_materials
    })


def my_requests(request):
    requests = MaterialAllocation.objects.filter(
        allocated_by=request.user
    ).order_by('-id')

    return render(request, "dashboard/my_requests.html", {"requests": requests})



def admin_material_requests(request):

    pending_requests = MaterialAllocation.objects.filter(
        status='pending'
    ).order_by('-id')

    history_list = MaterialAllocation.objects.exclude(
        status='pending'
    ).order_by('-id')

    paginator = Paginator(history_list, 10)
    page_number = request.GET.get('page')
    history = paginator.get_page(page_number)

    if request.method == "POST":
        req_id = request.POST.get("request_id")
        action = request.POST.get("action")

        req = get_object_or_404(MaterialAllocation, id=req_id)

        admin_user = request.user
        requester = getattr(req.allocated_by, 'user', req.allocated_by) if req.allocated_by else None

        if action == "approve":
            try:
                with transaction.atomic():

                    # 🔹 STOCK CHECK & DEDUCT
                    stock, _ = Stock.objects.get_or_create(material=req.material, defaults={'quantity': 0})
                    if stock.quantity < req.quantity:
                        raise ValueError(f"Not enough stock for {req.material.name}. Available: {stock.quantity}, Requested: {req.quantity}")

                    stock.quantity -= req.quantity
                    stock.save()

                    # 🔹 UPDATE STATUS
                    req.status = "approved"
                    req.save(update_fields=["status"])

                    # 🔹 CALCULATE COST & CREATE EXPENSE
                    unit_price = req.material.unit_price or 0
                    total_cost = req.quantity * unit_price

                    if total_cost > 0:
                        report, created = ExpenseReport.objects.get_or_create(
                            project=req.project,
                            expense_date=date.today(),
                            category='materials',
                            defaults={
                                "submitted_by": admin_user,
                                "notes": f"Material allocation expenses for {req.project.title}"
                            }
                        )

                        ExpenseItem.objects.create(
                            report=report,
                            description=f"{req.material.name} ({req.quantity} {req.material.unit})",
                            amount=total_cost
                        )

                # 🔹 NOTIFICATION (SUCCESS)
                if requester:
                    create_notification(
                        recipient=requester,
                        sender=admin_user,
                        title="Material Request Approved",
                        message=f"{req.material.name} ({req.quantity}) approved for {req.project.title}.",
                        category="material"
                    )

                messages.success(request, f"Material request for {req.material.name} ({req.quantity}) approved successfully.")
                return redirect('admin_material_requests')

            except ValueError as e:

                # 🔹 NOTIFICATION (ERROR)
                create_notification(
                    recipient=admin_user,
                    sender=admin_user,
                    title="Approval Failed",
                    message=str(e),
                    category="error"
                )

                messages.error(request, str(e))
                return render(request, "dashboard/admin/material_requests.html", {
                    "pending_requests": pending_requests,
                    "history": history,
                    "error": str(e)
                })

        elif action == "reject":

            req.status = "rejected"
            req.save(update_fields=["status"])

            if requester:
                create_notification(
                    recipient=requester,
                    sender=admin_user,
                    title="Material Request Rejected",
                    message=f"{req.material.name} ({req.quantity}) rejected for {req.project.title}.",
                    category="material"
                )

            messages.warning(request, f"Material request for {req.material.name} rejected.")
            return redirect('admin_material_requests')

    return render(request, "dashboard/admin/material_requests.html", {
        "pending_requests": pending_requests,
        "history": history
    })


# ===============================
# BOM / KIT ASSIGNMENT
# ===============================
@login_required(login_url='/users/login')
def assign_kit_to_project(request, pid):
    from projects.models import Project
    project = get_object_or_404(Project, pk=pid)
    
    if request.method == 'POST':
        kit_id = request.POST.get('kit_id')
        if kit_id:
            kit = get_object_or_404(KitConfiguration, id=kit_id)
            # Create Material Allocations for each item in the kit
            for item in kit.items.all():
                # Check if allocation already exists
                allocation, created = MaterialAllocation.objects.get_or_create(
                    project=project,
                    material=item.material,
                    defaults={
                        'quantity': item.quantity,
                        'allocated_by': request.user,
                        'status': 'pending'
                    }
                )
                if not created:
                    allocation.quantity += item.quantity
                    allocation.save()
                    
            messages.success(request, f'Successfully assigned BOM Template: {kit.name} to {project.title}')
        return redirect('project_detail', pid=project.id)
        
    kits = KitConfiguration.objects.filter(is_active=True)
    return render(request, 'dashboard/admin/assign_kit.html', {'project': project, 'kits': kits})


# ===============================
# FEATURE 13: PROCUREMENT INTELLIGENCE (RFQ)
# ===============================

@login_required(login_url='/users/login')
def rfq_list(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        project_id = request.POST.get('project_id')
        due_date = request.POST.get('due_date')
        status = request.POST.get('status', 'published')

        material_ids = request.POST.getlist('material_id[]')
        quantities = request.POST.getlist('quantity[]')
        target_prices = request.POST.getlist('target_price[]')

        if not title or not due_date:
            messages.error(request, 'RFQ Title and Due Date are required.')
            return redirect('rfq_list')

        project = None
        if project_id:
            try:
                from projects.models import Project
                project = Project.objects.get(id=project_id)
            except:
                pass

        rfq = RequestForQuotation.objects.create(
            title=title,
            project=project,
            due_date=due_date,
            status=status,
            created_by=request.user
        )

        item_count = 0
        for mid, qty, tp in zip(material_ids, quantities, target_prices):
            if mid and qty:
                mid_str = str(mid).strip()
                if mid_str.isdigit():
                    mat_obj = Material.objects.filter(id=int(mid_str)).first()
                else:
                    mat_obj = Material.objects.filter(name__iexact=mid_str).first()
                    if not mat_obj:
                        mat_obj = Material.objects.create(
                            name=mid_str,
                            unit="Units",
                            minimum_stock=5
                        )
                        Stock.objects.get_or_create(material=mat_obj, defaults={'quantity': 0})

                if mat_obj:
                    RFQItem.objects.create(
                        rfq=rfq,
                        material=mat_obj,
                        quantity=int(qty),
                        target_price=float(tp) if tp else None
                    )
                    item_count += 1

        messages.success(request, f'RFQ #{rfq.id:04d} "{rfq.title}" created with {item_count} items.')
        return redirect('rfq_detail', rfq_id=rfq.id)

    rfqs = RequestForQuotation.objects.all().order_by('-created_at')
    from projects.models import Project
    projects = Project.objects.all().order_by('title')
    materials = Material.objects.all().order_by('name')

    return render(request, 'dashboard/procurement/rfq_list.html', {
        'rfqs': rfqs,
        'projects': projects,
        'materials': materials,
        'now': timezone.now()
    })

@login_required(login_url='/users/login')
def rfq_detail(request, rfq_id):
    rfq = get_object_or_404(RequestForQuotation, id=rfq_id)
    quotations = rfq.quotations.all().order_by('total_amount')
    
    if quotations.exists():
        # Auto-detect L1 (Lowest Bidder)
        l1_quote = quotations.first()
        if not l1_quote.is_l1:
            VendorQuotation.objects.filter(rfq=rfq).update(is_l1=False)
            l1_quote.is_l1 = True
            l1_quote.save(update_fields=['is_l1'])

    vendors = Vendor.objects.all().order_by('name')

    context = {
        'rfq': rfq,
        'quotations': quotations,
        'vendors': vendors
    }
    return render(request, 'dashboard/procurement/rfq_detail.html', context)

@login_required(login_url='/users/login')
def add_vendor_quotation(request, rfq_id):
    rfq = get_object_or_404(RequestForQuotation, id=rfq_id)
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor_id')
        delivery_days = request.POST.get('delivery_days', 7)
        payment_terms = request.POST.get('payment_terms', 'Standard')

        if not vendor_id:
            messages.error(request, 'Please select a vendor.')
            return redirect('rfq_detail', rfq_id=rfq.id)

        vendor = get_object_or_404(Vendor, id=vendor_id)

        quote = VendorQuotation.objects.create(
            rfq=rfq,
            vendor=vendor,
            delivery_days=int(delivery_days) if delivery_days else 7,
            payment_terms=payment_terms,
            status='submitted'
        )

        total = 0
        for item in rfq.items.all():
            price = request.POST.get(f'item_price_{item.id}')
            if price:
                u_price = float(price)
                QuotationItem.objects.create(
                    quotation=quote,
                    rfq_item=item,
                    unit_price=u_price
                )
                total += item.quantity * u_price

        quote.total_amount = total
        quote.save(update_fields=['total_amount'])

        if rfq.status in ['draft', 'published']:
            rfq.status = 'evaluating'
            rfq.save(update_fields=['status'])

        messages.success(request, f'Quotation from {vendor.name} (Total: ₹{total:,.2f}) added successfully.')

    return redirect('rfq_detail', rfq_id=rfq.id)

@login_required(login_url='/users/login')
def award_rfq(request, rfq_id, quote_id):
    rfq = get_object_or_404(RequestForQuotation, id=rfq_id)
    quote = get_object_or_404(VendorQuotation, id=quote_id, rfq=rfq)
    
    # Update statuses
    rfq.status = 'closed'
    rfq.save(update_fields=['status'])
    
    VendorQuotation.objects.filter(rfq=rfq).update(status='rejected')
    quote.status = 'accepted'
    quote.save(update_fields=['status'])
    
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
    
    messages.success(request, f"RFQ Awarded to {quote.vendor.name}! Purchase Order PO-{po.id} generated.")
    return redirect('purchase_order_detail', oid=po.id)
