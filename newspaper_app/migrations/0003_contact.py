# Generated by Django 4.2.3 on 2023-07-27 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newspaper_app', '0002_post_tag_remove_post_category_post_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
