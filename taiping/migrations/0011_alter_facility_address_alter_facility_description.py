# Generated by Django 5.2.3 on 2025-06-11 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiping', '0010_remove_courseclass_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facility',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='facility',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
