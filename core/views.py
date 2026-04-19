from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.cache import cache
import csv
from .models import Student, Faculty, Department, Dorm, Room
from .forms import StudentForm, FacultyForm, DepartmentForm, DormForm, RoomForm

def dashboard(request):
    cache_key = 'dashboard_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = {
            'total_students': Student.objects.count(),
            'total_faculties': Faculty.objects.count(),
            'total_dorms': Dorm.objects.count(),
            'total_rooms': Room.objects.count(),
        }
        cache.set(cache_key, stats, 300)
    
    recent_students = Student.objects.select_related('faculty', 'department', 'dorm', 'room').order_by('-created_at')[:5]
    
    faculties = Faculty.objects.annotate(student_count=Count('students')).order_by('-student_count')[:5]
    dorms = Dorm.objects.annotate(student_count=Count('students')).order_by('-student_count')[:5]
    
    context = {
        'stats': stats,
        'recent_students': recent_students,
        'faculties': faculties,
        'dorms': dorms,
    }
    return render(request, 'core/dashboard.html', context)

def student_list(request):
    search_query = request.GET.get('q', '')
    faculty_filter = request.GET.get('faculty', '')
    dorm_filter = request.GET.get('dorm', '')
    year_filter = request.GET.get('year', '')
    
    students = Student.objects.select_related('faculty', 'department', 'dorm', 'room')
    
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(father_name__icontains=search_query) |
            Q(faculty__faculty_name__icontains=search_query)
        )
    
    if faculty_filter:
        students = students.filter(faculty_id=faculty_filter)
    
    if dorm_filter:
        students = students.filter(dorm_id=dorm_filter)
    
    if year_filter:
        students = students.filter(admission_year=year_filter)
    
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    faculties = Faculty.objects.all()
    dorms = Dorm.objects.all()
    years = Student.objects.values_list('admission_year', flat=True).distinct().order_by('-admission_year')
    
    context = {
        'page_obj': page_obj,
        'faculties': faculties,
        'dorms': dorms,
        'years': years,
        'search_query': search_query,
    }
    return render(request, 'core/student_list.html', context)

@csrf_protect
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, 'زده کوونکي اضافه شو!')
            cache.delete('dashboard_stats')
            return redirect('student_list')
    else:
        form = StudentForm()
    
    faculties = Faculty.objects.all()
    dorms = Dorm.objects.all()
    return render(request, 'core/add_student.html', {'form': form, 'faculties': faculties, 'dorms': dorms})

@csrf_protect
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'زده کوونکي تغیر شو!')
            cache.delete('dashboard_stats')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    
    faculties = Faculty.objects.all()
    departments = Department.objects.filter(faculty=student.faculty)
    dorms = Dorm.objects.all()
    rooms = Room.objects.filter(dorm=student.dorm) if student.dorm else []
    
    context = {
        'form': form,
        'student': student,
        'faculties': faculties,
        'departments': departments,
        'dorms': dorms,
        'rooms': rooms,
    }
    return render(request, 'core/edit_student.html', context)

@require_POST
@csrf_protect
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    messages.success(request, 'زده کوونکی حذف شو!')
    cache.delete('dashboard_stats')
    return redirect('student_list')

def get_departments(request):
    faculty_id = request.GET.get('faculty_id')
    if faculty_id:
        departments = Department.objects.filter(faculty_id=faculty_id).values('id', 'department_name')
        return JsonResponse(list(departments), safe=False)
    return JsonResponse([], safe=False)

def get_rooms(request):
    dorm_id = request.GET.get('dorm_id')
    if dorm_id:
        rooms = Room.objects.filter(dorm_id=dorm_id)
        room_list = []
        for room in rooms:
            is_full = room.current_students_count >= room.capacity
            room_list.append({
                'id': room.id,
                'room_number': room.room_number,
                'capacity': room.capacity,
                'current_count': room.current_students_count,
                'is_full': is_full,
            })
        return JsonResponse(room_list, safe=False)
    return JsonResponse([], safe=False)

def get_available_rooms(request):
    dorm_id = request.GET.get('dorm_id')
    if dorm_id:
        rooms = Room.objects.filter(dorm_id=dorm_id)
        room_list = []
        for room in rooms:
            if not room.is_full:
                room_list.append({
                    'id': room.id,
                    'room_number': room.room_number,
                    'available': room.capacity - room.current_students_count,
                })
        return JsonResponse(room_list, safe=False)
    return JsonResponse([], safe=False)

def id_card(request, pk):
    student = get_object_or_404(Student.objects.select_related('faculty', 'department', 'dorm', 'room'), pk=pk)
    return render(request, 'core/id_card.html', {'student': student})

def reports(request):
    faculty_id = request.GET.get('faculty')
    dorm_id = request.GET.get('dorm')
    year = request.GET.get('year')
    
    students = Student.objects.select_related('faculty', 'department', 'dorm', 'room')
    
    if faculty_id:
        students = students.filter(faculty_id=faculty_id)
    if dorm_id:
        students = students.filter(dorm_id=dorm_id)
    if year:
        students = students.filter(admission_year=year)
    
    faculties = Faculty.objects.all()
    dorms = Dorm.objects.all()
    years = Student.objects.values_list('admission_year', flat=True).distinct().order_by('-admission_year')
    
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'faculties': faculties,
        'dorms': dorms,
        'years': years,
    }
    return render(request, 'core/reports.html', context)

def export_csv(request):
    faculty_id = request.GET.get('faculty')
    dorm_id = request.GET.get('dorm')
    year = request.GET.get('year')
    
    students = Student.objects.select_related('faculty', 'department', 'dorm', 'room')
    
    if faculty_id:
        students = students.filter(faculty_id=faculty_id)
    if dorm_id:
        students = students.filter(dorm_id=dorm_id)
    if year:
        students = students.filter(admission_year=year)
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    # ✅ ONLY FIX (UTF-8 BOM for Excel)
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['نوم', 'د پلار نوم', 'ولایت', 'ولسوالۍ', 'پوهنځی', 'څانګه', 'کلاس', ' فیصدي', 'منرل', 'اطاق', 'د کارت نمبر', 'د داخلې کال'])
    
    for student in students:
        writer.writerow([
            student.name,
            student.father_name,
            student.province,
            student.district,
            student.faculty.faculty_name,
            student.department.department_name,
            student.class_level,
            student.percentage,
            student.dorm.dorm_name if student.dorm else '',
            student.room.room_number if student.room else '',
            student.card_number,
            student.admission_year,
        ])
    
    return response

def faculty_list(request):
    faculties = Faculty.objects.annotate(student_count=Count('students'))
    return render(request, 'core/faculty_list.html', {'faculties': faculties})

@csrf_protect
def add_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'پوهنځی اضافه شوه')
            return redirect('faculty_list')
    else:
        form = FacultyForm()
    return render(request, 'core/add_faculty.html', {'form': form})

@require_POST
@csrf_protect
def delete_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    faculty.delete()
    messages.success(request, 'پوهنځی حذف شوه')
    return redirect('faculty_list')

def department_list(request):
    departments = Department.objects.select_related('faculty').annotate(student_count=Count('students'))
    return render(request, 'core/department_list.html', {'departments': departments})

@csrf_protect
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'څانګه اضافه شوه')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    faculties = Faculty.objects.all()
    return render(request, 'core/add_department.html', {'form': form, 'faculties': faculties})

@require_POST
@csrf_protect
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.delete()
    messages.success(request, 'څانګه حذف شوه')
    return redirect('department_list')

def dorm_list(request):
    dorms = Dorm.objects.annotate(student_count=Count('students'), room_count=Count('rooms'))
    return render(request, 'core/dorm_list.html', {'dorms': dorms})

@csrf_protect
def add_dorm(request):
    if request.method == 'POST':
        form = DormForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'منزل اضافه شوو')
            return redirect('dorm_list')
    else:
        form = DormForm()
    return render(request, 'core/add_dorm.html', {'form': form})

@require_POST
@csrf_protect
def delete_dorm(request, pk):
    dorm = get_object_or_404(Dorm, pk=pk)
    dorm.delete()
    messages.success(request, 'منزل حذف شوو')
    return redirect('dorm_list')

def room_list(request):
    rooms = Room.objects.select_related('dorm').annotate(student_count=Count('students'))
    return render(request, 'core/room_list.html', {'rooms': rooms})

@csrf_protect
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطاق اضافه شوو')
            return redirect('room_list')
    else:
        form = RoomForm()
    dorms = Dorm.objects.all()
    return render(request, 'core/add_room.html', {'form': form, 'dorms': dorms})

@require_POST
@csrf_protect
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    room.delete()
    messages.success(request, 'اطاق حذف شوو')
    return redirect('room_list')