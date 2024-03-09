# Generated by Django 4.2.9 on 2024-03-09 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("Completed", "Completed"),
                    ("Accepted", "Accepted"),
                    ("Cancelled", "Cancelled"),
                    ("New", "New"),
                ],
                default="New",
                max_length=10,
            ),
        ),
    ]
