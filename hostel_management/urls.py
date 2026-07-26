from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from core import views
from core.views import backup_database

urlpatterns = [
    # Admin (Jazzmin automatically apply کېږي)
    path('admin/', admin.site.urls),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:pk>/', views.delete_student, name='delete_student'),
    path('students/id-card/<int:pk>/', views.id_card, name='id_card'),

    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_csv, name='export_csv'),

    # Faculties
    path('faculties/', views.faculty_list, name='faculty_list'),
    path('faculties/add/', views.add_faculty, name='add_faculty'),
    path('faculties/delete/<int:pk>/', views.delete_faculty, name='delete_faculty'),

    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/delete/<int:pk>/', views.delete_department, name='delete_department'),

    # Dorms
    path('dorms/', views.dorm_list, name='dorm_list'),
    path('dorms/add/', views.add_dorm, name='add_dorm'),
    path('dorms/delete/<int:pk>/', views.delete_dorm, name='delete_dorm'),

    # Rooms
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/add/', views.add_room, name='add_room'),
    path('rooms/delete/<int:pk>/', views.delete_room, name='delete_room'),

    # API
    path('api/get-departments/', views.get_departments, name='get_departments'),
    path('api/get-rooms/', views.get_rooms, name='get_rooms'),
    path('api/get-available-rooms/', views.get_available_rooms, name='get_available_rooms'),

    # Backup
    path('backup/', backup_database, name='backup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)