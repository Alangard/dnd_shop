# Generated by Django 4.2.9 on 2024-04-10 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0028_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Completed', 'Completed'), ('Accepted', 'Accepted'), ('Cancelled', 'Cancelled')], default='New', max_length=10),
        ),
    ]
