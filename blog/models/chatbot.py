from django.db import models
from django.contrib.auth.models import User

class InputChatbot(models.Model):
    query = models.TextField(null=True)
    answer = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query[:10]


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploaded_docs/')
    tokens_total = models.PositiveIntegerField(null=True)
    tokens_useful = models.PositiveIntegerField(null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

