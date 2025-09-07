from django.db import models

class RunPlaybook(models.Model):
    playbook = models.CharField(max_length=250)
    

