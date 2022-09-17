from django.db import models

# Create your models here.
class BotUser(models.Model):
    name = models.CharField(max_length=255, default='')
    username = models.CharField(max_length=255, default='')
    user_id = models.CharField(max_length=255, default='')
    access_token = models.CharField(max_length=255, default='', blank=True)
    instagram_account_id = models.CharField(max_length=255, default='', blank=True)
    channel_id = models.CharField(max_length=255, default='', blank=True)
    status = models.CharField(max_length=255, default='')
    extra_status = models.CharField(max_length=255, default='', blank=True)
    smth_url = models.CharField(max_length=255, default='', blank=True)
    smth_txt = models.CharField(max_length=255, default='', blank=True)
    response_id = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.name


# for telegram channels
class Channels_info(models.Model):
    title = models.CharField(max_length=255, default='')
    username = models.CharField(max_length=255, default='')
    user_id = models.CharField(max_length=255, default='')
    user_type = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=255, default='', blank=True)
    can_post_messages = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.title
