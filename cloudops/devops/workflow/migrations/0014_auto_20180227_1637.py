# Generated by Django 2.0.1 on 2018-02-27 16:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workflow', '0013_cronapplycomment_projectapplycomment_projectmemberapplycomment_projectreleaseapplycomment_projectuse'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('depart_name', models.CharField(max_length=100, verbose_name='部门名称')),
                ('depart_director', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='部门负责人')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.project', verbose_name='项目')),
            ],
            options={
                'verbose_name_plural': '部门',
            },
        ),
        migrations.AlterField(
            model_name='authority_flow',
            name='status',
            field=models.IntegerField(choices=[(0, '不通过'), (1, '待审批'), (2, '部门负责人审批通过'), (3, '权限变更完成')], help_text='0 不通过, 1 待审批, 2 部门负责人审批通过, 3 已执行', verbose_name='状态'),
        ),
    ]
