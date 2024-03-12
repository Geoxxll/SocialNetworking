# Generated by Django 5.0.2 on 2024-03-12 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialNetworking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='num_likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='like',
            name='author_like',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_likes', to='socialNetworking.author'),
        ),
        migrations.AlterField(
            model_name='like',
            name='like_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_likes', to='socialNetworking.post'),
        ),
    ]
