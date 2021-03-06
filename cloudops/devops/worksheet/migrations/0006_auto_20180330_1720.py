# Generated by Django 2.0.1 on 2018-03-30 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('worksheet', '0005_auto_20180329_1420'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorksheetCommunicate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pepole', models.IntegerField(choices=[(0, '用户'), (1, '客服')], verbose_name='发表人')),
                ('content', models.TextField(verbose_name='内容')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='发表时间')),
            ],
            options={
                'db_table': 'worksheet_communicate',
            },
        ),
        migrations.AlterField(
            model_name='worksheet',
            name='status',
            field=models.IntegerField(choices=[(0, '已关闭'), (4, '待审批'), (1, '未受理'), (2, '待处理'), (3, '已处理')], verbose_name='状态'),
        ),
        migrations.AddField(
            model_name='worksheetcommunicate',
            name='worksheet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='worksheet.WorkSheet', verbose_name='工单'),
        ),
    ]
