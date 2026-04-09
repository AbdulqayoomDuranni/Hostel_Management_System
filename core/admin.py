from django.contrib import admin
from .models import Student, Faculty, Department, Dorm, Room

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['faculty_name']
    search_fields = ['faculty_name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department_name', 'faculty']
    list_filter = ['faculty']
    search_fields = ['department_name']

@admin.register(Dorm)
class DormAdmin(admin.ModelAdmin):
    list_display = ['dorm_name']
    search_fields = ['dorm_name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'dorm', 'capacity']
    list_filter = ['dorm']
    search_fields = ['room_number']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'father_name', 'faculty', 'department', 'dorm', 'room', 'card_number', 'admission_year']
    list_filter = ['faculty', 'department', 'dorm', 'admission_year']
    search_fields = ['name', 'father_name', 'card_number']
    readonly_fields = ['created_at']
