# Generated by Django 3.2 on 2021-04-21 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20210409_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameboard',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='gameboard',
            name='winner',
            field=models.CharField(default='0', max_length=1),
        ),
    ]
