from django.db import models
from django.contrib.auth.models import User
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64



class Writer(models.Model):
    #user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="writer")
    name = models.CharField(max_length=200)
    createdDate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return u'%s' % (self.name)


class Article(models.Model):
    text_title = models.CharField(max_length=50, null=True, blank=True)
    text = models.TextField(max_length=200, null=True, blank=True)
    refWriter = models.ForeignKey(Writer, on_delete=models.CASCADE)
    createdDate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return u'[%s] : %s' % (self.refWriter,self.text_title)



def generate_chart():
    # Sample data
    labels = ['Technology', 'Lifestyle', 'Education', 'News']
    values = [10, 15, 7, 5]

    # Create the figure
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title('Posts by Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Number of Posts')

    # Save the figure to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Encode the bytes as base64 for rendering in HTML
    graph = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return graph