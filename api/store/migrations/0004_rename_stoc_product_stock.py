# Generated by Django 4.2.9 on 2024-02-08 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0003_rename_stock_product_stoc"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="stoc",
            new_name="stock",
        ),
    ]
