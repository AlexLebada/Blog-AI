# Generated by Django 4.2.16 on 2024-12-25 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_alter_photo_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to='uploaded_photos/'),
        ),
    ]