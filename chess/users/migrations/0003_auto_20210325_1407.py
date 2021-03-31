# Generated by Django 3.1.7 on 2021-03-25 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210325_1401'),
        ('users', '0002_user_currentgame'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='currentGame',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='api.gameboard'),
        ),
    ]