# Generated by Django 4.2.7 on 2024-03-25 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_product_stock_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(default='Automated Type', max_length=100),
        ),
    ]