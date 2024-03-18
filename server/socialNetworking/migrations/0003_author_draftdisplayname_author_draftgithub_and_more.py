# Generated by Django 5.0.2 on 2024-03-18 05:44

import django.utils.timezone
import socialNetworking.models.authors
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialNetworking', '0002_alter_comment_comment_author_alter_comment_post_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='draftDisplayName',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='author',
            name='draftGithub',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='author',
            name='draftProfileImage',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=socialNetworking.models.authors.get_draft_upload_path),
        ),
        migrations.AddField(
            model_name='author',
            name='profileImagePicture',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=socialNetworking.models.authors.get_upload_path),
        ),
        migrations.AlterField(
            model_name='comment',
            name='published_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
