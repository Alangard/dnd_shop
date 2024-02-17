from typing import Any
from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password',
    }))

    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'email', 'password', 'confirm_password']


    def clean(self):
        cleanned_data = super(RegistrationForm, self).clean()
        password = cleanned_data.get('password')
        confirm_password = cleanned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Password does not match!')


    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for field  in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = f'Enter {field.replace("_", " ").title()}'
    

        
