from django import forms
from .models import *
class CycleForm(forms.ModelForm):
    class Meta:
        model = Cycle
        fields = ['start_date', 'end_date', 'average_symptoms']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

from django.contrib.auth.models import User
from django_select2.forms import Select2Widget
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
class DateOfBirthForm(forms.Form):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))

class CountryForm(forms.Form):
    country = CountryField(
        blank_label="(Select your country)"
    ).formfield(
        widget=CountrySelectWidget
    )

from django.contrib.auth.password_validation import validate_password

class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Must meet the password Strength requirements."
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Run Django's password validators (raises ValidationError on failure)
        validate_password(password)
        return password

class ConditionsForm(forms.Form):
    conditions = forms.ModelMultipleChoiceField(
        queryset=Condition.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

class OvulationForm(forms.Form):
    last_ovulation = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))

class CycleTypeForm(forms.Form):
    cycle_type = forms.ChoiceField(
        choices=[('regular','Regular'),('irregular','Irregular'),('unknown','Unknown')]
    )

class CycleLengthForm(forms.Form):
    cycle_length = forms.IntegerField(min_value=21, label="Length of last cycle (days)")

class PeriodLengthForm(forms.Form):
    period_length = forms.IntegerField(min_value=3, label="Duration of last menstrual period (days)")

class PreferencesForm(forms.Form):
    OPTIONS = [
      ('cycle','Cycle Tracking'),
      ('symptoms','Symptom Logging'),
      ('pregnancy','Pregnancy & Sexual Behavior'),
      ('diet','Diet & Meal Recommendations'),
      ('hormone','Hormone Tracking & Recommendations'),
    ]
    preferences = forms.MultipleChoiceField(
      choices=OPTIONS,
      widget=forms.CheckboxSelectMultiple
    )

FORMS = [
    ('dob',      DateOfBirthForm),
    ('country',  CountryForm),
    ('username', UsernameForm),
    ('conditions', ConditionsForm),
    ('ovulation', OvulationForm),
    ('type',     CycleTypeForm),
    ('length',   CycleLengthForm),
    ('period',   PeriodLengthForm),
    ('prefs',    PreferencesForm),
]

# core/forms.py

from django import forms
from .models import DailyEntry

class RangeSliderInput(forms.widgets.Input):
    input_type = 'range'

    def __init__(self, min=0, max=5, step=1, attrs=None):
        default = {'min': min, 'max': max, 'step': step}
        if attrs:
            default.update(attrs)
        super().__init__(attrs=default)

class DailyEntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        # Exclude profile (your FK), not 'cycle'
        exclude = ['profile', 'date', 'last_updated', 'needs_review']
        widgets = {
            'cramps':         RangeSliderInput(),
            'bloating':       RangeSliderInput(),
            'tender_breasts': RangeSliderInput(),
            'headache':       RangeSliderInput(),
            'acne':           RangeSliderInput(),
            'mood':           RangeSliderInput(),
            'stress':         RangeSliderInput(),
            'energy':         RangeSliderInput(),
            'sleep_quality':  RangeSliderInput(),
            'libido':         RangeSliderInput(),
        }
class ProfileForm(forms.ModelForm):
    medical_conditions = forms.ModelMultipleChoiceField(
        queryset=Condition.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Medical Conditions"
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date of Birth"
    )
    country = forms.ChoiceField(
        choices=Profile._meta.get_field('country').choices,
        widget=CountrySelectWidget,
        label="Country"
    )

    class Meta:
        model = Profile
        exclude = ['user']  # user handled by view
        widgets = {
            'last_ovulation': forms.DateInput(attrs={'type': 'date'}),
            'cycle_type': forms.Select(),
            'cycle_length': forms.NumberInput(attrs={'min': 1}),
            'period_length': forms.NumberInput(attrs={'min': 1}),
            'preferences': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. tracking, symptoms, diet'}),
        }