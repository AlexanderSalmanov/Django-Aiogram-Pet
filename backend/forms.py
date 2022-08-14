from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Enter your username:')
    password = forms.CharField(max_length=100, label='Enter your password:', widget=forms.PasswordInput())
