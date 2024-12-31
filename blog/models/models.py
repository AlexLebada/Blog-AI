from django.db import models
from django.contrib.auth.models import User
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64



class Writer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="writer")
    pseudo_name = models.CharField(max_length=200)
    all_posts = models.PositiveIntegerField(null=True, blank=True)
    votes = models.PositiveIntegerField(null=True,blank=True)
    tokens_used = models.PositiveIntegerField(null=True)
    tokens_available = models.PositiveIntegerField(null=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return u'%s' % (self.user)


class Article(models.Model):
    text_title = models.CharField(max_length=50, null=True, blank=True)
    text = models.TextField(max_length=200, null=True, blank=True)
    refWriter = models.ForeignKey(Writer, on_delete=models.CASCADE)
    createdDate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return u'[%s] : %s' % (self.refWriter,self.text_title)

