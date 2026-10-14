from django import forms
from .models import *

class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = [
            "project",
            "invoice_number",
            "issue_date",
            "due_date",
            "total_amount",
            "status",
            "notes",
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_project'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. INV-2026-001', 'id': 'id_invoice_number'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_issue_date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_due_date'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg fw-bold text-success', 'placeholder': '0.00', 'step': '0.01', 'id': 'id_total_amount'}),
            'status': forms.Select(attrs={'class': 'form-select', 'id': 'id_status'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add payment instructions, bank NEFT/RTGS details, or customer notes...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f"Select {field.label or field_name.replace('_', ' ').title()}"
        if 'project' in self.fields and user:
            from projects.access import get_user_accessible_projects
            qs = get_user_accessible_projects(user)
            if self.instance and self.instance.pk and getattr(self.instance, 'project_id', None):
                from projects.models import Project
                qs = (qs | Project.objects.filter(pk=self.instance.project_id)).distinct()
            self.fields['project'].queryset = qs


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = [
            "invoice",
            "payment_date",
            "amount",
            "method",
            "received_by",
            "notes",
        ]
        widgets = {
            'invoice': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_invoice'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_payment_date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-lg fw-bold text-success', 'placeholder': '0.00', 'step': '0.01', 'id': 'id_amount'}),
            'method': forms.Select(attrs={'class': 'form-select', 'id': 'id_method'}),
            'received_by': forms.Select(attrs={'class': 'form-select', 'id': 'id_received_by'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Transaction reference number, UTR number, or payment remarks...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f"Select {field.label or field_name.replace('_', ' ').title()}"


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = ExpenseReport
        fields = ['project', 'expense_date', 'category', 'notes']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f"Select {field.label or field_name.replace('_', ' ').title()}"
        if 'project' in self.fields and user:
            from projects.access import get_user_accessible_projects
            qs = get_user_accessible_projects(user)
            if self.instance and self.instance.pk and getattr(self.instance, 'project_id', None):
                from projects.models import Project
                qs = (qs | Project.objects.filter(pk=self.instance.project_id)).distinct()
            self.fields['project'].queryset = qs


class ExpenseItemForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount', 'step':'0.01'}),
        }

class ExpenseReceiptForm(forms.ModelForm):

    class Meta:
        model = ExpenseReceipt
        fields = ["file"]

        widgets = {
            "file": forms.ClearableFileInput(attrs={
                "class": "form-control"
            })
        }
class ProjectCostingForm(forms.ModelForm):
    class Meta:
        model = ProjectCosting
        fields = ['panels_cost', 'inverter_cost', 'structure_cost', 'bos_cost', 'cable_cost', 'earthing_lightning_cost', 'labour_cost', 'logistics_cost', 'installation_overhead', 'commission_cost', 'contingency_cost', 'gst_percentage', 'selling_price']
        widgets = {
            field: forms.NumberInput(attrs={'class': 'form-control text-end cost-input', 'step': '0.01'}) for field in fields
        }
