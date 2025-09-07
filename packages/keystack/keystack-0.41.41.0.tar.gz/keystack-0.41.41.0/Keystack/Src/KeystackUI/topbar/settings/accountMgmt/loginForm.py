from django.contrib.auth.models import User
from django import forms

'''
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)
'''

from django.contrib.auth.forms import UserCreationForm

#UserModel = get_user_model()

from django.db import models

class UserLoginForm(forms.ModelForm):
    #firstName = forms.CharField(label='first_name')
    #lastName = forms.CharField(label='last_name')
    #username = forms.CharField(label='username')
    loginName = forms.CharField(max_length=50, required=True, label='loginName', widget=forms.TextInput(
         attrs={'placeholder':'Login Name', 'id':'loginName'}))

    #email = forms.EmailField(label='email')
    #email = forms.EmailField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder':'Email', 'id':'email'}), label='email')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password', 'autocomplete': 'off'}), label='password')

    # When view's login() calls is_valid(), it will come here
    # to clean up and authenticate user exists and credentials.
    '''
    def cleaned(self, *args, **kwargs):
        cleanedData = super(UserLoginForm, self).cleaned()
        #email = self.cleaned_data['email']
        loginName = self.cleaned_data['loginName']
        password = self.cleaned_data['password']

        if loginName and password:
            user = authenticate(username=loginName, password=password)
            #userAuth = authenticate(email=email, password=password)
            #userQuery = User.objects.filter(username=username)
            #if userQuery.count() == 1:
            #    user = userQuery.first()

            if not userAuth:
                raise forms.ValidationError('User does not exists')

            if not user.check_password('password'):
                raise forms.ValidationError('Incorrect password')

            if not user.is_active():
                raise forms.ValidationError('This user is no longer active')
            
        return super(UserLoginForm, self).clean(*args, **kwargs)
    '''
    
    class Meta(UserCreationForm):
        model = User
        #fields = ['email', 'password']
        fields = ['loginName', 'password']

'''
class UserForm(forms.ModelForm):
    # Including widget=xxx will not display password in readable text.
    #firstName = forms.CharField(label='firstName')
    #lastName = forms.CharField(label='lastName')
    password = forms.CharField(widget=forms.PasswordInput)
    #email = forms.EmailField(label='email')

    # Information about your class
    #class Meta(UserCreationForm):
    #    model = User
    #    fields = ['firstName', 'lastName', 'password', 'email']
'''
