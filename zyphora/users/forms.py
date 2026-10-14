from django import forms
from .models import *
import datetime


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique username (max 20 chars)', 'required': 'required'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique email address', 'required': 'required'})
    )
    role = forms.ChoiceField(
        required=True,
        choices=[
            ('', 'Select Role'),
            ('manager', 'Sales Manager'),
            ('sales', 'Sales Executive'),
            ('engineer', 'Installer / Engineer'),
            ('accountant', 'Accounts'),
            ('liaison', 'Liaison Officer'),
            ('procurement', 'Procurement'),
            ('partner', 'Channel Partner / Dealer'),
            ('staff', 'Staff'),
        ],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'role-select', 'required': 'required'})
    )
    date_joined = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d']
    )

    class Meta:
        model = Employee
        exclude = ['user', 'profile_pic']
        widgets = {
            'access_level': forms.Select(choices=[
                ('', 'Select Access Level'),
                ('billing', 'Billing Only'),
                ('salary', 'Salary Management'),
                ('full', 'Full Financial Access')
            ])
        }

    def __init__(self, *args, **kwargs):

        role = kwargs.pop('role', None)   # ✅ remove role before super()
        super().__init__(*args, **kwargs)

        import datetime

        # For editing existing employee, user credentials are not required in this form
        if self.instance and self.instance.pk:
            if 'username' in self.fields:
                self.fields['username'].required = False
                if hasattr(self.instance, 'user') and self.instance.user:
                    self.fields['username'].initial = self.instance.user.username
            if 'email' in self.fields:
                self.fields['email'].required = False
                if hasattr(self.instance, 'user') and self.instance.user:
                    self.fields['email'].initial = self.instance.user.email
            if 'role' in self.fields:
                self.fields['role'].required = False
                if hasattr(self.instance, 'user') and self.instance.user:
                    self.fields['role'].initial = self.instance.user.role

        # Bootstrap styling & empty label for select fields
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                if field_name == 'supervisor':
                    field.empty_label = 'Select Supervisor / Reporting Manager'
                else:
                    field.empty_label = f"Select {field.label or field_name.replace('_', ' ').title()}"

            if field_name == 'is_active':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['role', 'access_level', 'supervisor']:
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Default date
        if not self.instance.date_joined:
            self.fields['date_joined'].initial = datetime.date.today()

        # Hide fields based on role
        if role == 'engineer':
            if 'access_level' in self.fields:
                self.fields['access_level'].widget = forms.HiddenInput()
            if 'supervisor' in self.fields:
                self.fields['supervisor'].widget = forms.HiddenInput()

        elif role == 'accountant':
            if 'specialization' in self.fields:
                self.fields['specialization'].widget = forms.HiddenInput()
            if 'supervisor' in self.fields:
                self.fields['supervisor'].widget = forms.HiddenInput()

        elif role in ['sales', 'staff', 'manager', 'procurement', 'partner']:
            if 'specialization' in self.fields:
                self.fields['specialization'].widget = forms.HiddenInput()
            if 'access_level' in self.fields:
                self.fields['access_level'].widget = forms.HiddenInput()

        elif role == 'liaison':
            if 'specialization' in self.fields:
                self.fields['specialization'].widget = forms.HiddenInput()
            if 'access_level' in self.fields:
                self.fields['access_level'].widget = forms.HiddenInput()
            if 'supervisor' in self.fields:
                self.fields['supervisor'].widget = forms.HiddenInput()

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not self.instance.pk:
            if not username:
                raise forms.ValidationError("Username is required.")
            if len(username) > 20:
                raise forms.ValidationError("Username cannot exceed 20 characters.")
            if CustomUser.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError(f"Username '{username}' is already taken. Please choose another username.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not self.instance.pk:
            if not email:
                raise forms.ValidationError("Email is required.")
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError(f"Email '{email}' is already registered with another account.")
        return email

    def clean_role(self):
        role = self.cleaned_data.get('role', '')
        if not self.instance.pk and not role:
            raise forms.ValidationError("Please select a role.")
        return role
        

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'username',
            'email'
        ]