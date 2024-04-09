# Generated by Django 4.2.9 on 2024-04-09 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('New', 'New'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='New', max_length=10),
        ),
    ]
