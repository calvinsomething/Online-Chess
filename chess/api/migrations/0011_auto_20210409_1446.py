# Generated by Django 3.1.7 on 2021-04-09 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20210408_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameboard',
            name='winner',
            field=models.CharField(default=0, max_length=1),
        ),
        migrations.AlterField(
            model_name='gameboard',
            name='captured',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]