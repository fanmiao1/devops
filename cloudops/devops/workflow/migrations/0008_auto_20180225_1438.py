# Generated by Django 2.0.1 on 2018-02-25 14:38

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0007_auto_20180225_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project_releaseflow',
            name='testingreport',
            field=tinymce.models.HTMLField(max_length=2000, verbose_name='测试报告'),
        ),
    ]
