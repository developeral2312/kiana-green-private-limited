from django import forms
from .models import *
from users.models import CustomUser


# ---------------- Project Forms ----------------
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['slug', 'lead', 'created_at', 'updated_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'revenue': forms.NumberInput(attrs={'class': 'form-control'}),
            'engineer': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['engineer'].queryset = Employee.objects.filter(user__role="engineer", is_active=True)
        self.fields['engineer'].empty_label = 'Select Engineer'


class ProjectActivityForm(forms.ModelForm):
    class Meta:
        model = ProjectActivity
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Activity title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Activity details'}),
        }


from django import forms
from .models import ProjectMedia, InstallationTask, WorkReport, ServiceReport, InstallationIssue

class ProjectMediaForm(forms.ModelForm):
    class Meta:
        model = ProjectMedia
        fields = ['project', 'caption', 'category', 'installation_task', 'work_report', 'service_report', 'issue']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a caption'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'installation_task': forms.Select(attrs={'class': 'form-select'}),
            'work_report': forms.Select(attrs={'class': 'form-select'}),
            'service_report': forms.Select(attrs={'class': 'form-select'}),
            'issue': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f"Select {field.label or field_name.replace('_', ' ').title()}"

        project_id = self.data.get('project') or self.initial.get('project')

        if self.user and 'project' in self.fields:
            from projects.access import get_user_accessible_projects
            self.fields['project'].queryset = get_user_accessible_projects(self.user)

        if self.user and 'installation_task' in self.fields:
            qs = self.fields['installation_task'].queryset.filter(assigned_to=self.user)
            if project_id:
                qs = qs.filter(project_id=project_id)
            self.fields['installation_task'].queryset = qs

        category = self.data.get('category') or self.initial.get('category')
        self.hide_fields_for_category(category)

    def hide_fields_for_category(self, category):
        if category == 'installation_photo':
            for field in ['work_report', 'service_report', 'issue']:
                self.fields[field].widget = forms.HiddenInput()
        elif category == 'issue_photo':
            for field in ['installation_task', 'work_report', 'service_report']:
                self.fields[field].widget = forms.HiddenInput()


# ---------------- Task Form ----------------
class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d']
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task title', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Task description'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # For newly created tasks, status is optional and defaults to 'new'
        if not self.instance.pk:
            if 'status' in self.fields:
                self.fields['status'].required = False
                self.fields['status'].initial = 'new'

        # Restrict assignment dropdown based on role
        if user:
            if not (user.is_superuser or user.role in ['admin', 'manager', 'director', 'engineer']):
                self.fields.pop('assigned_to', None)
            else:
                self.fields['assigned_to'].queryset = CustomUser.objects.filter(is_active=True).order_by('first_name', 'username')
                self.fields['assigned_to'].required = True
        else:
            if 'assigned_to' in self.fields:
                self.fields['assigned_to'].queryset = CustomUser.objects.filter(is_active=True).order_by('first_name', 'username')

        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].empty_label = 'Select User'


# ---------------- Service Forms ----------------
class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['project', 'title', 'description', 'requested_by', 'assigned_to',]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the service'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'requested_by': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if 'project' in self.fields:
            self.fields['project'].empty_label = 'Select Project'
            if self.user:
                from projects.access import get_user_accessible_projects
                self.fields['project'].queryset = get_user_accessible_projects(self.user)
        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].empty_label = 'Select User'
        if 'requested_by' in self.fields:
            self.fields['requested_by'].empty_label = 'Select User'


class ServiceReportForm(forms.ModelForm):
    class Meta:
        model = ServiceReport
        fields = ['report_text', 'images']
        widgets = {
            'report_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter service report details'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ---------------- Installation Forms ----------------
class InstallationTaskForm(forms.ModelForm):
    class Meta:
        model = InstallationTask
        fields = ['step', 'status', 'notes']
        widgets = {
            'step': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



class InstallationIssueForm(forms.ModelForm):
    class Meta:
        model = InstallationIssue
        fields = ['project', 'title', 'description', 'image']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short issue title (e.g., Panel crack)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the issue clearly...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if 'project' in self.fields:
            self.fields['project'].empty_label = 'Select Project'
            if self.user:
                from projects.access import get_user_accessible_projects
                self.fields['project'].queryset = get_user_accessible_projects(self.user)


# ---------------- Work Report ----------------
class WorkReportForm(forms.ModelForm):
    class Meta:
        model = WorkReport
        fields = [
            'project',
            'work_type',
            'title',
            'description',
            'status',
            'date',
            'before_image',
            'after_image',
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional title'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the work done...'}),
            'before_image': forms.FileInput(attrs={'class': 'form-control'}),
            'after_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if 'project' in self.fields:
            self.fields['project'].empty_label = 'Select Project'
            if self.user:
                from projects.access import get_user_accessible_projects
                self.fields['project'].queryset = get_user_accessible_projects(self.user)


class EquipmentSerialForm(forms.ModelForm):
    class Meta:
        model = EquipmentSerial
        fields = ['category', 'brand', 'model_name', 'serial_number', 'installation_date', 'warranty_months', 'status', 'notes']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Waaree, Luminous'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 540W Mono PERC'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Serial No.'}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
