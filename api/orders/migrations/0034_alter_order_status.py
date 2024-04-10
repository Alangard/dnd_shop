# Generated by Django 4.2.9 on 2024-04-10 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0033_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed'), ('Accepted', 'Accepted')], default='New', max_length=10),
        ),
    ]
