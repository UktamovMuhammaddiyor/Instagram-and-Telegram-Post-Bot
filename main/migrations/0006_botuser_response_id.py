# Generated by Django 4.0.3 on 2022-04-12 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_botuser_smth_txt'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='response_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]