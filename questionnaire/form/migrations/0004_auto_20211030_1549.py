# Generated by Django 3.0.5 on 2021-10-30 07:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0003_auto_20211030_1515'),
    ]

    operations = [
        migrations.RenameField(
            model_name='choice',
            old_name='qid',
            new_name='question',
        ),
    ]
