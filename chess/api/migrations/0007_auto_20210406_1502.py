# Generated by Django 3.1.7 on 2021-04-06 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_gameboard_captured'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gameboard',
            old_name='checkMate',
            new_name='check',
        ),
    ]