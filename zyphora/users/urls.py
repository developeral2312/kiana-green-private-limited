from django.urls import path
from .views import *



urlpatterns = [
    path('login/',login_page,name='login'),
    path('logout/',logout_page,name='logout'),

    path('dashboard/',dashboard,name='dashboard'),
    path('admin/',admin_dashboard,name='admin'),
    path('engineer/',engineer_dashboard,name='engineer'),
    path('accountant/',accountant_dashboard,name='accountant'),
    path('sales/',sales_dashboard,name='sales'),
    path('manager/',sales_dashboard,name='manager'),
    path('staff/',staff_dashboard,name='staff'),
    path('liaison/',liaison_dashboard,name='liaison'),
    path('subcontractor/',subcontractor_dashboard_view,name='subcontractor'),
    path('partner/',dashboard,name='partner'),

    path('admin-profile/', admin_profile, name='admin_profile'),
    path('change-password/',ChangePassword.as_view(),name='password'),
    path('addemp/',add_employee,name='addemp'),
    path('emplist/',all_employees,name='emplist'),
    path('view-emp/<int:emp_id>/',view_employee,name='viewemp'),
    path('edit-emp/<int:emp_id>/',edit_employee,name='editemp'),

    path('profile/',view_profile,name='profile'),
    path('edit-profile/',edit_profile,name='edit_profile'),

    path('blog/',blog_list,name='blogposts'),
    path('add-post/',add_post,name='addpost'),
    path('view-post/<int:id>/',view_post,name='viewpost'),
    path('edit-post/<int:bid>/',edit_post,name='editpost'),
    path('delete-post/<int:bid>/',delete_post,name='deletepost'),
    
    path('mark-as-read/<int:nid>/', mark_as_read, name='mark_as_read'),
    path('mark-all-as-read/', mark_all_as_read, name='mark_all_as_read'),
    path('notification-data/',get_notifications,name='notification_data'),
    path('notifications/', notifications, name='notifications'),
    path('delete-notification/<int:nid>/',delete_notification,name='delete_notification'),
    path('delete-all-notifications/', delete_all_notifications, name='delete_all_notifications'),
    path('notify/<int:id>/',notifyEmployee,name='notify'),

    # HR / STAFF MANAGEMENT
    path('hr/dashboard/', hr_dashboard, name='hr_dashboard'),
    path('hr/attendance/mark/', mark_attendance, name='mark_attendance'),
    path('hr/leave/apply/', apply_leave, name='apply_leave'),
    path('hr/leave/approve/<int:pk>/', approve_leave, name='approve_leave'),

    # APPROVAL ENGINE
    path('approvals/', approval_dashboard, name='approval_dashboard'),
    path('approvals/approve/<int:pk>/', approve_request, name='approve_request'),
    path('approvals/reject/<int:pk>/', reject_request, name='reject_request'),
]