# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django_countries.fields import CountryField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    country = CountryField()
    medical_conditions = models.ManyToManyField('Condition', blank=True)
    last_ovulation = models.DateField(null=True, blank=True)
    cycle_type = models.CharField(
        max_length=10,
        choices=[('regular','Regular'),('irregular','Irregular'),('unknown','Unknown')]
    )
    cycle_length = models.PositiveSmallIntegerField(null=True, blank=True)
    period_length = models.PositiveSmallIntegerField(null=True, blank=True)#mentraulation days
    preferences = models.JSONField(default=list, blank=True)
    profile_image=models.ImageField(upload_to='profile_images/', default='profile_images/default.png')
    # Additional fields can be added as needed
    def __str__(self):
        return self.user.username
    
class Condition(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Cycle(models.Model):
    PHASE_CHOICES = [
        ('menstrual', 'Menstrual'),
        ('follicular', 'Follicular'),
        ('ovulation', 'Ovulation'),
        ('luteal', 'Luteal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    predicted_next_start = models.DateField(null=True, blank=True)
    cycle_length = models.PositiveIntegerField(editable=False)
    average_symptoms = models.JSONField(default=dict, blank=True)
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='menstrual')
    
    
    # Automated tracking fields
    last_updated = models.DateTimeField(auto_now=True)
    needs_review = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s cycle {self.start_date} to {self.end_date}"

    def save(self, *args, **kwargs):
        # Calculate cycle length before saving
        self.cycle_length = (self.end_date - self.start_date).days
        super().save(*args, **kwargs)
    
    def duration(self):
        return self.cycle_length
    
    def update_phase(self):
        # Implement phase calculation logic based on cycle days
        pass
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', 'start_date']),
        ]

class DailyEntry(models.Model):
    CERVICAL_MUCUS_CHOICES = [
        ('none', 'None'),
        ('sticky', 'Sticky'),
        ('watery', 'Watery'),
        ('egg-white', 'Egg-White'),
        ('creamy', 'Creamy'),
        ('atypical', 'Atypical'),
    ]
    
    profile = models.ForeignKey(Profile, related_name='daily_entries', on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, related_name='daily_entries', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    
    # Physical Symptoms
    cramps = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    bloating = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    tender_breasts = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    headache = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    acne = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    
    # Emotional Symptoms
    mood = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=3
    )
    stress = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    energy = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=3
    )
    
    # Cervical Observations
    cervical_mucus = models.CharField(
        max_length=20,
        choices=CERVICAL_MUCUS_CHOICES,
        default='none'
    )
    
    # Additional Metrics
    sleep_quality = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=3
    )
    libido = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=2
    )
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.profile.user.username}'s entry for {self.date}"
    
    class Meta:
          unique_together = ['profile', 'date']
          ordering = ['date']
          verbose_name_plural = 'Daily Entries'


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction_date = models.DateField()
    predicted_start = models.DateField()
    confidence = models.FloatField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)

    def accuracy(self):
        if self.actual_start:
            return abs((self.predicted_start - self.actual_start).days)
        return None 
       
    def __str__(self):
        return f"{self.user.username}'s prediction for {self.predicted_start}"

#demo
class DemoRequest(models.Model):
    email       = models.EmailField()
    datetime    = models.DateTimeField(null=True, blank=True)
    message     = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} <{self.email}> @ {self.created_at:%Y-%m-%d %H:%M}"