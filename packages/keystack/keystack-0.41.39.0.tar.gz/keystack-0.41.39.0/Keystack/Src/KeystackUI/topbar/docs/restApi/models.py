from django.db import models

class RunPlaybookModel(models.Model):
    playbook = models.CharField(max_length=255, blank=False)
    sessionId = models.CharField(max_length=255, blank=True)
    awsS3 = models.CharField(max_length=255, blank=True)
    jira = models.CharField(max_length=255, blank=True)
    trackResults = models.CharField(max_length=255, blank=True)
    emailResults = models.CharField(max_length=255, blank=True)
    s3BucketUri = models.CharField(max_length=255, blank=True)
    awsAccessKey = models.CharField(max_length=255, blank=True)
    awsSecretKey = models.CharField(max_length=255, blank=True)
    awsRegion = models.CharField(max_length=255, blank=True)
    #age = models.IntegerField()

    def __str__(self):
        return self.playbook

