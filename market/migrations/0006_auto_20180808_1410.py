# Generated by Django 2.1 on 2018-08-08 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_auto_20180808_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.ImageField(upload_to='static/covers/'),
        ),
    ]
