# Generated by Django 3.0.5 on 2021-10-30 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0002_auto_20211030_1513'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='options',
        ),
        migrations.AddField(
            model_name='question',
            name='type',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
    ]