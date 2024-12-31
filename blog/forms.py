from django import forms
from ckeditor.widgets import CKEditorWidget
from .models.posts import Post
from .models.chatbot import InputChatbot


class ChatbotForm(forms.ModelForm):
    class Meta:
        model = InputChatbot
        fields = ['query', 'answer']


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Post
        fields = ['content', 'title', 'slug', 'summary', 'category', 'image']


