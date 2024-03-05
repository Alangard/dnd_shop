# Generated by Django 4.2.9 on 2024-03-05 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0011_alter_order_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("Completed", "Completed"),
                    ("New", "New"),
                    ("Cancelled", "Cancelled"),
                    ("Accepted", "Accepted"),
                ],
                default="New",
                max_length=10,
            ),
        ),
    ]
