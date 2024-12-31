from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models.models import Writer
#pip install django-ckeditor
from ckeditor.fields import RichTextField


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('tech', 'Technology'),
        ('life', 'Lifestyle'),
        ('edu', 'Education'),
        ('news', 'News'),
    ]
    STATUS = [
        ('no_status', 'no_status'),
        ('for_approval', 'for_approval'),
        ('approved', 'approved'),
    ]

    title = models.CharField(max_length=255, default="noTitle")
    slug = models.SlugField(max_length=255, unique=True)
    summary = models.CharField(max_length=300)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    content = RichTextField()
    published = models.BooleanField(default=True)
    status = models.CharField(max_length=15, choices=STATUS, default="no_status")
    likes = models.PositiveIntegerField(null=True)
    #writer = models.ForeignKey(Writer, on_delete=models.SET_NULL, null=True)
    writer = models.ForeignKey(Writer, blank=True, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='img', null=True,  default='placeholder.png')

    # special class to def metadata
    class Meta:
        ordering = ['-created']

        def __unicode__(self): #returns the Post object's title
            return u'%s'% self.title

    def __str__(self):
        return u'%s' % (self.title)

    def get_absolute_url(self): # returns URL that doesnt change ?
        return reverse('blog.views.post', args=[self.slug])

