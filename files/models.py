from django.db import models

import boto3

class Image(models.Model):
	name = models.CharField(max_length=50)
	path = models.TextField()
	uploaded_by = models.CharField(max_length=10, null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	excluded = BooleanField(default=False)

    @property
    def url(self):
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        s3_signed_url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket':'ao-prime-bucket',
                        'Key': self.path})
        return s3_signed_url