from django.db import models

# Create your models here.


class UserModel(models.Model):
    fullName = models.CharField(max_length=50)
    loginName = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    #userRole = models.CharField(max_length=50)
    
    userRoleRadioChoices = [('admin','Admin'), ('manager','Manager'), ('engineer', 'Engineer')]
    userRole = models.CharField(choices=userRoleRadioChoices, max_length=10)

    def __str__(self):
        return self.fullName
    
    class Meta:
        # Mongo collection table name
        # In views, obj = UserModel.objects.all() returns all the document defined in __str__ (self.fullName)
       db_table = 'accountMgmt'
    
    