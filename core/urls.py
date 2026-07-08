from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),

    # Admin Panel Pages
    path('admin/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Admin Actions
    path('admin/project/add/', views.add_project, name='add_project'),
    path('admin/project/edit/<int:pk>/', views.edit_project, name='edit_project'),
    path('admin/project/delete/<int:pk>/', views.delete_project, name='delete_project'),
    path('admin/message/read/<int:pk>/', views.mark_message_read, name='mark_message_read'),
    path('admin/message/delete/<int:pk>/', views.delete_message, name='delete_message'),
    path('admin/profile/update/', views.update_profile, name='update_profile'),
]
