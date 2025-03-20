from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import FileInput

from userauths.models import User, Profile
class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter Full Name"}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter Username"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':"Enter Email"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter Phone Number"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':"Enter Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':"Confirm Password"}))
    class Meta:
        model = User
        fields = ['full_name','username','email','phone','password1','password2']

class UserUpateForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields=[
           "image",
           "full_name",
            "phone",
           "gender",
            "country",
            "city",
            "state",
           "address",

        ]

        widgets= {
            'image':FileInput(attrs={"onchange" :"loadFile(event)","class":"upload"})
        }