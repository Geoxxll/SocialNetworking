# Generated by Django 5.0.2 on 2024-03-26 11:32

import django.db.models.deletion
import django.utils.timezone
import socialNetworking.models.authors
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('type', models.CharField(default='author', editable=False, max_length=15)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('url', models.URLField()),
                ('host', models.URLField()),
                ('displayName', models.CharField(max_length=100)),
                ('github', models.URLField(blank=True, null=True)),
                ('profileImagePicture', models.ImageField(blank=True, default=None, null=True, upload_to=socialNetworking.models.authors.get_upload_path)),
                ('draftProfileImage', models.ImageField(blank=True, default=None, null=True, upload_to=socialNetworking.models.authors.get_draft_upload_path)),
                ('draftDisplayName', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('draftGithub', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('profileImage', models.URLField(blank=True, null=True)),
                ('lastCommitFetch', models.DateTimeField(blank=True, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(null=True)),
                ('type', models.CharField(default='comment', editable=False, max_length=15)),
                ('comment', models.TextField()),
                ('contentType', models.CharField(default='text/markdown', editable=False, max_length=20)),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('num_likes', models.IntegerField(default=0)),
                ('comment_author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='socialNetworking.author')),
                ('likes', models.ManyToManyField(blank=True, related_name='comment_likes', to='socialNetworking.author')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='socialNetworking.comment')),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='commentInbox',
            field=models.ManyToManyField(blank=True, to='socialNetworking.comment'),
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='follow', editable=False, max_length=15)),
                ('summary', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('actor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actor_follow_set', to='socialNetworking.author')),
                ('object_of_follow', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='object_of_follow_set', to='socialNetworking.author')),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='followInbox',
            field=models.ManyToManyField(blank=True, to='socialNetworking.follow'),
        ),
        migrations.CreateModel(
            name='InboxItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='inbox item', editable=False, max_length=15)),
                ('items_object_id', models.UUIDField()),
                ('items_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='inbox', editable=False, max_length=15)),
                ('inbox_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialNetworking.author')),
                ('item', models.ManyToManyField(related_name='inbox', to='socialNetworking.inboxitem')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='like', editable=False, max_length=15)),
                ('summary', models.TextField(blank=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('object', models.URLField(null=True)),
                ('author_like', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_likes', to='socialNetworking.author')),
                ('like_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='socialNetworking.comment')),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='likeInbox',
            field=models.ManyToManyField(blank=True, to='socialNetworking.like'),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('host_url', models.URLField(primary_key=True, serialize=False)),
                ('api_url', models.URLField()),
                ('username_out', models.CharField(max_length=20)),
                ('password_out', models.CharField(max_length=20)),
                ('approved', models.BooleanField(default=True)),
                ('node_user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('shared_body', models.TextField(blank=True, null=True)),
                ('title', models.CharField(max_length=100)),
                ('type', models.CharField(default='post', editable=False, max_length=15)),
                ('post_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField()),
                ('source', models.URLField()),
                ('origin', models.URLField()),
                ('description', models.TextField(blank=True, null=True)),
                ('contentType', models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='text/plain', max_length=30)),
                ('content', models.BinaryField(blank=True, null=True)),
                ('visibility', models.CharField(choices=[('PUBLIC', 'Public'), ('FRIENDS', 'Friends'), ('UNLISTED', 'Unlisted')], default='PUBLIC', max_length=10)),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('shared_on', models.DateTimeField(blank=True, null=True)),
                ('num_likes', models.IntegerField(default=0)),
                ('author_of_posts', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts_set', to='socialNetworking.author')),
                ('likes', models.ManyToManyField(blank=True, related_name='likes', to='socialNetworking.author')),
                ('shared_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-published_at', '-shared_on'],
            },
        ),
        migrations.AddField(
            model_name='like',
            name='like_post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_likes', to='socialNetworking.post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='socialNetworking.post'),
        ),
        migrations.AddField(
            model_name='author',
            name='postInbox',
            field=models.ManyToManyField(blank=True, to='socialNetworking.post'),
        ),
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='follower', editable=False, max_length=15)),
                ('followed_at', models.DateTimeField(auto_now_add=True)),
                ('followee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followee_set', to='socialNetworking.author')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower_set', to='socialNetworking.author')),
            ],
            options={
                'unique_together': {('follower', 'followee')},
            },
        ),
    ]
