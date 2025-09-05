_I='emailForm'
_H='Re-enter Password'
_G='captchaForm'
_F='captcha'
_E='Password'
_D='Email'
_C='id'
_B='form-control'
_A='class'
from django import forms
from datetime import datetime
class ConnexionForm(forms.Form):email=forms.EmailField(label=_D,widget=forms.TextInput(attrs={_A:_B}));password=forms.CharField(label=_E,widget=forms.PasswordInput(attrs={_A:_B}))
class RegistrationTestForm(forms.Form):firstName=forms.CharField(label='First Name',max_length=30,widget=forms.TextInput(attrs={_A:_B}));lastName=forms.CharField(label='Last Name',max_length=30,widget=forms.TextInput(attrs={_A:_B}));email=forms.EmailField(label=_D,max_length=50,widget=forms.TextInput(attrs={_A:_B}));password=forms.CharField(label=_E,widget=forms.PasswordInput(attrs={_A:_B}));password_confirmation=forms.CharField(label=_H,widget=forms.PasswordInput(attrs={_A:_B}));code=forms.CharField(label='SpartaQube password',widget=forms.PasswordInput(attrs={_A:_B}))
class RegistrationBaseForm(RegistrationTestForm):captcha=forms.CharField(label=_F,widget=forms.TextInput(attrs={_A:_B,_C:_G}))
class RegistrationForm(RegistrationBaseForm):code=forms.CharField(label='Guest code',max_length=100,widget=forms.PasswordInput(attrs={_A:_B}),required=True)
class ResetPasswordForm(forms.Form):email=forms.EmailField(label=_D,widget=forms.TextInput(attrs={_A:_B,_C:_I}));captcha=forms.CharField(label=_F,widget=forms.TextInput(attrs={_A:_B,_C:_G}))
class ResetPasswordChangeForm(forms.Form):token=forms.CharField(label='Code',widget=forms.TextInput(attrs={_A:_B,_C:'tokenForm'}));password=forms.CharField(label=_E,widget=forms.PasswordInput(attrs={_A:_B}));password_confirmation=forms.CharField(label=_H,widget=forms.PasswordInput(attrs={_A:_B}));captcha=forms.CharField(label=_F,widget=forms.TextInput(attrs={_A:_B,_C:_G}));email=forms.EmailField(label=_D,widget=forms.TextInput(attrs={_A:_B,_C:_I}))