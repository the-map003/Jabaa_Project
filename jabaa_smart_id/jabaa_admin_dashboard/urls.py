from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_citizen_data/', views.get_citizen_data, name='get_citizen_data'),
    path('signup_view/', views.signup_view, name="signup_view"),
    path('login_view/', views.login_view, name="login_view"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('logout/', views.logout_view, name='logout'),
    path('manage_accounts/', views.manage_accounts, name='manage_accounts'),
    path('update-staff/<int:staff_id>/', views.update_staff, name='update_staff'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('add-citizen/', views.add_citizen, name='add_citizen'),
    path('manage-citizen/', views.manage_citizen, name='manage_citizen'),  # Fixed
    path('edit-citizen/<int:citizen_id>/', views.edit_citizen, name='edit_citizen'),
    path('delete-citizen/<int:citizen_id>/', views.delete_citizen, name='delete_citizen'),
]
