# Generated by Django 4.0.3 on 2022-04-12 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_botuser_access_token_alter_botuser_channel_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='smth_txt',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
