# Generated by Django 2.1 on 2018-08-06 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_auto_20180806_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='market.Customer'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='market.Book'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='score',
            field=models.PositiveSmallIntegerField(choices=[('★☆☆☆☆', 1), ('★★☆☆☆', 2), ('★★★☆☆', 3), ('★★★★☆', 4), ('★★★★★', 5)]),
        ),
    ]
