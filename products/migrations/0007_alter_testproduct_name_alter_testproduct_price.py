# Generated by Django 5.1 on 2024-10-23 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_testproduct_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testproduct',
            name='name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='testproduct',
            name='price',
            field=models.TextField(),
        ),
    ]
