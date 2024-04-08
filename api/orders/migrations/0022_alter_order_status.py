# Generated by Django 4.2.9 on 2024-04-05 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Accepted', 'Accepted'), ('New', 'New')], default='New', max_length=10),
        ),
    ]
