# Generated by Django 4.2.7 on 2024-04-04 10:36

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_alter_cartorder_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartorderitems',
            name='image',
            field=models.ImageField(default='product.jpg', upload_to=core.models.user_directory_path),
        ),
    ]
