# Generated by Django 5.0.2 on 2024-02-23 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialNetworking', '0010_alter_author_github'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='profileImage',
            field=models.URLField(blank=True, null=True),
        ),
    ]
