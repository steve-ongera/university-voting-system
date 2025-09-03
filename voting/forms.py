# voting/forms.py
from django import forms
from django.core.validators import RegexValidator
from .models import Student, Delegate, Candidate

class LoginForm(forms.Form):
    registration_number = forms.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[A-Z]{2}\d{3}/\d{4}/\d{4}$',
            message='Registration number must be in format: SC211/0530/2022'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your registration number (e.g., SC211/0530/2022)',
            'autofocus': True
        }),
        label='Registration Number'
    )
    
    birth_certificate_number = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your birth certificate number'
        }),
        label='Birth Certificate Number'
    )

class DelegateVoteForm(forms.Form):
    delegate = forms.ModelChoiceField(
        queryset=Delegate.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )
    
    def __init__(self, department=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if department:
            self.fields['delegate'].queryset = Delegate.objects.filter(
                department=department,
                is_approved=True
            ).select_related('student', 'party')

class MainVoteForm(forms.Form):
    candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )
    
    def __init__(self, position=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if position:
            self.fields['candidate'].queryset = Candidate.objects.filter(
                position=position,
                is_approved=True
            ).select_related('student', 'party')
