# Generated by Django 5.0.7 on 2024-07-21 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiping', '0003_course_sort_order_coursegroup_sort_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
