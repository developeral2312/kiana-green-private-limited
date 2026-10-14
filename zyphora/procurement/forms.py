from django import forms
from django.db.models import Q
from projects.models import Project
from .models import *




class MaterialForm(forms.ModelForm):

    class Meta:
        model = Material
        exclude = ['created_at']

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "minimum_stock": forms.NumberInput(attrs={"class": "form-control"}),
        }


class VendorForm(forms.ModelForm):

    class Meta:
        model = Vendor
        exclude = ['created_at']

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Tata Power Solar / Waaree Ltd"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Rahul Sharma (Sales Manager)"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 9876543210"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "sales@vendor.com"}),
            "gst_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "22AAAAA0000A1Z5"}),
            "pan_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "AAAAA0000A"}),
            "category": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Solar Modules, Inverters, Structures, Cables"}),
            "payment_terms": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 30 Days Credit, 50% Advance"}),
            "bank_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. HDFC Bank"}),
            "bank_account_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 50200012345678"}),
            "bank_ifsc": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. HDFC0001234"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Complete business address"}),
        }




class PurchaseOrderForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrder
        exclude = ['total_amount','created_at']

        widgets = {
            "vendor": forms.Select(attrs={"class": "form-select"}),
            "order_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "expected_delivery": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f"Select {field.label or field_name.replace('_', ' ').title()}"



class PurchaseOrderItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrderItem
        exclude = ['purchase_order']


        widgets = {
            "material": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f"Select {field.label or field_name.replace('_', ' ').title()}"



class GoodsReceivedForm(forms.ModelForm):

    class Meta:
        model = GoodsReceived
        exclude = ['created_at']


        widgets = {
            "purchase_order": forms.Select(attrs={"class": "form-select"}),
            "received_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "received_by": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f"Select {field.label or field_name.replace('_', ' ').title()}"



class ProjectModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        proj_type = obj.get_project_type_display() if hasattr(obj, 'get_project_type_display') else ''
        loc = f" — {obj.location}" if obj.location else ""
        type_str = f" ({proj_type})" if proj_type else ""
        return f"{obj.title}{type_str}{loc}"


class MaterialAllocationRequestForm(forms.ModelForm):
    project = ProjectModelChoiceField(
        queryset=Project.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="-- Select Project --"
    )
    material_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "list": "warehouse-materials-list",
            "placeholder": "Type or write material name..."
        })
    )

    class Meta:
        model = MaterialAllocation
        fields = ['project', 'quantity']   
        widgets = {
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        from projects.access import get_user_accessible_projects
        self.fields['project'].queryset = get_user_accessible_projects(user)


class MaterialAllocationForm(forms.ModelForm):
    project = ProjectModelChoiceField(
        queryset=Project.objects.none(),
        widget=forms.Select(attrs={"class": "form-select form-select-lg shadow-sm", "id": "id_project"}),
        empty_label="-- Select Assigned Project --"
    )
    material_name = forms.CharField(
        max_length=200,
        required=True,
        label="Warehouse Material / Hardware",
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg shadow-sm",
            "id": "id_material_name",
            "list": "warehouse-materials-list",
            "placeholder": "Type or write material / hardware name manually...",
            "autocomplete": "off"
        })
    )

    class Meta:
        model = MaterialAllocation
        fields = ['project', 'quantity']
        widgets = {
            "quantity": forms.NumberInput(attrs={
                "class": "form-control form-control-lg shadow-sm",
                "id": "id_quantity",
                "placeholder": "Enter quantity required",
                "min": "1"
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        from projects.access import get_user_accessible_projects
        self.fields['project'].queryset = get_user_accessible_projects(user)


        