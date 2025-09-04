from rest_framework import serializers
from .models import RunPlaybookModel

'''
class RunPlaybookSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunPlaybookModel
        # fields = ('playbook', 'sessionId', 'awsS3', 'jira', 'trackResults',
        #           'emailResults', 's3BucketUri', 'awsAccessKey', 'awsSecretKey',
        #           'awsRegion')
        fields = '__all__'
'''
 
from rest_framework import serializers       
class RunPlaybookSerializer(serializers.Serializer):
    playbook     = serializers.CharField(required=True, help_text="The Playbook name")
    sessionId    = serializers.CharField(required=False)
    awsS3        = serializers.CharField(required=False)
    jira         = serializers.CharField(required=False)
    emailResults = serializers.CharField(required=False)
    trackResults = serializers.CharField(required=False)
    awsAccessKey = serializers.CharField(required=False)
    awsSecretKey = serializers.CharField(required=False)
    awsRegion    = serializers.CharField(required=False)
    s3BucketName = serializers.CharField(required=False)