# Generated by Django 4.2.9 on 2024-02-17 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="phone_number",
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
    ]
