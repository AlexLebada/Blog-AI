# Generated by Django 4.2.16 on 2024-12-29 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_rename_name_writer_pseudo_name_writer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='writer',
            name='all_posts',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='writer',
            name='votes',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
