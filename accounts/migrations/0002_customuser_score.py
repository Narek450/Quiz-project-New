# Generated by Django 4.2.2 on 2023-06-29 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
