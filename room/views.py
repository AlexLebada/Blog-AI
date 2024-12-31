from django.shortcuts import render


# Create your views here.
# blog/views.py
from django.shortcuts import redirect, render

from . import forms

#@login_required
def photo_upload(request):
    form = forms.PhotoForm()
    if request.method == 'POST':
        form = forms.PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            # set the uploader to the user before saving the model
            photo.uploader = request.user
            # now we can save
            photo.save()
            return redirect('photo_upload')
    return render(request, 'photo_upload.html', context={'form': form})