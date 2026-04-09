from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import os

def validate_image_size(image):
    limit = 200 * 1024
    if image.size > limit:
        raise ValidationError('تصویر сли نه تر ۲۰۰ کیلوبایت غواړي!')

def validate_image_extension(value):
    valid_extensions = ['jpg', 'jpeg', 'png']
    ext = os.path.splitext(value.name)[1].lower().replace('.', '')
    if ext not in valid_extensions:
        raise ValidationError('یوازې JPG یا PNG فورمت اجازه لري.')

class Faculty(models.Model):
    faculty_name = models.CharField(max_length=100, unique=True, verbose_name='د پوهنځی نوم')
    
    class Meta:
        verbose_name = 'پوهنځی'
        verbose_name_plural = 'پوهنځی'
        ordering = ['faculty_name']
    
    def __str__(self):
        return self.faculty_name

class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    department_name = models.CharField(max_length=100, verbose_name='د برخې نوم')
    
    class Meta:
        verbose_name = 'برخه'
        verbose_name_plural = 'برخې'
        ordering = ['department_name']
        unique_together = ['faculty', 'department_name']
    
    def __str__(self):
        return f"{self.faculty.faculty_name} - {self.department_name}"

class Dorm(models.Model):
    dorm_name = models.CharField(max_length=100, unique=True, verbose_name='د خواب نوم')
    
    class Meta:
        verbose_name = 'خواب'
        verbose_name_plural = 'خوابونه'
        ordering = ['dorm_name']
    
    def __str__(self):
        return self.dorm_name

class Room(models.Model):
    room_number = models.CharField(max_length=20, verbose_name='د اطاق نمبر')
    dorm = models.ForeignKey(Dorm, on_delete=models.CASCADE, related_name='rooms')
    capacity = models.IntegerField(default=4, verbose_name='ظرفیت')
    
    class Meta:
        verbose_name = 'اطاق'
        verbose_name_plural = 'اطاقونه'
        ordering = ['dorm', 'room_number']
        unique_together = ['dorm', 'room_number']
    
    def __str__(self):
        return f"{self.dorm.dorm_name} - {self.room_number}"
    
    @property
    def current_students_count(self):
        return self.students.count()
    
    @property
    def is_full(self):
        return self.current_students_count >= self.capacity

class Student(models.Model):
    name = models.CharField(max_length=100, verbose_name='نوم')
    father_name = models.CharField(max_length=100, verbose_name='د پلار نوم')
    province = models.CharField(max_length=50, verbose_name='ولایت')
    district = models.CharField(max_length=50, verbose_name='ولسوالۍ')
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name='students')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='students')
    class_level = models.CharField(max_length=20, verbose_name='کلاس')
    percentage = models.FloatField(verbose_name="له څه حد څخه")
    dorm = models.ForeignKey(Dorm, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    photo = models.ImageField(
        upload_to='students/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size,
            validate_image_extension
        ],
        verbose_name='تصویر'
    )
    card_number = models.CharField(max_length=50, unique=True, verbose_name='د کارت نمبر')
    admission_year = models.CharField(max_length=10, verbose_name='د داخلې کال')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'زده کوونکی'
        verbose_name_plural = 'زده کوونکي'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['father_name']),
            models.Index(fields=['faculty']),
            models.Index(fields=['card_number']),
            models.Index(fields=['dorm']),
            models.Index(fields=['admission_year']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.card_number}"
    
    def clean(self):
        super().clean()
        if self.room and self.room.is_full:
            raise ValidationError({'room': f"اطاق {self.room.room_number} ډک دی!"})
    
    def save(self, *args, **kwargs):
        if self.room and self.room.is_full:
            if not self.pk:
                raise ValidationError(f"اطاق {self.room.room_number} ډک دی!")
        super().save(*args, **kwargs)
