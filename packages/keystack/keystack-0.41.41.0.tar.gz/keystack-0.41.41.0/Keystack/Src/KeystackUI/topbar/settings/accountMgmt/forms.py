from django import forms
from .models import UserModel

class UserForm(forms.ModelForm):
    class Meta:
        model = UserModel
        widgets = {
            'password': forms.PasswordInput(),
        }
        userRoleRadioChoices = [('admin','Admin'), ('manager','Manager'), ('engineer', 'Engineer')]
        userRole = forms.CharField(label='userRole', widget=forms.RadioSelect(choices=userRoleRadioChoices))
        #fields = ['FullName', 'LoginName', 'Password', 'UserRole', 'Email']
        fields = "__all__"
