# Generated by Django 2.0.1 on 2018-02-27 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usercenter', '0005_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='depart_director',
        ),
        migrations.RemoveField(
            model_name='department',
            name='project',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='department',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='Department',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]