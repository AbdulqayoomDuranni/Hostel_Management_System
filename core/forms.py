from django import forms
from .models import Student, Faculty, Department, Dorm, Room
from django.core.exceptions import ValidationError

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نوم'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'د پلار نوم'}),
            'province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ولایت'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ولسوالۍ'}),
            'faculty': forms.Select(attrs={'class': 'form-select', 'id': 'id_faculty'}),
            'department': forms.Select(attrs={'class': 'form-select', 'id': 'id_department'}),
            'class_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'صنف'}),
            'percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'فیصدي'}),
            'dorm': forms.Select(attrs={'class': 'form-select', 'id': 'id_dorm'}),
            'room': forms.Select(attrs={'class': 'form-select', 'id': 'id_room'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'د کارت نمبر'}),
            'admission_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'د داخلې کال'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')

        if photo:
            # 10MB LIMIT
            if photo.size > 10 * 1024 * 1024:
                raise ValidationError(' image get than 10 MB ')

            # FILE TYPE CHECK
            ext = photo.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise ValidationError('یوازې JPG یا PNG فورمت اجازه لري.')

            # -------- IMAGE COMPRESSION --------
            img = Image.open(photo)

            output = BytesIO()

            # convert RGBA/P to RGB
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # resize (optional but recommended)
            max_size = (1080, 1080)
            img.thumbnail(max_size)

            # save compressed image
            img.save(output, format='JPEG', quality=60, optimize=True)

            output.seek(0)

            # replace original image
            photo = ContentFile(output.read(), name=photo.name)

        return photo

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')

        if room and room.is_full:
            if not self.instance.pk:
                raise ValidationError(f"اطاق {room.room_number} ډک دی")

        return cleaned_data


# ---------------- FACULTY ----------------
class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['faculty_name']
        widgets = {
            'faculty_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'د پوهنځی نوم'}),
        }


# ---------------- DEPARTMENT ----------------
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['faculty', 'department_name']
        widgets = {
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'department_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'د څانګي نوم'}),
        }


# ---------------- DORM ----------------
class DormForm(forms.ModelForm):
    class Meta:
        model = Dorm
        fields = ['dorm_name']
        widgets = {
            'dorm_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'د منرل نوم'}),
        }


# ---------------- ROOM ----------------
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'dorm', 'capacity']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'د اطاق نمبر'}),
            'dorm': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'value': 4}),
        }