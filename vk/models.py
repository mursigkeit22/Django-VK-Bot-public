import datetime

from django.db import models
from django.utils import timezone

from vk.helpers import five_minutes_ago


class Chat(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    local_id = models.BigIntegerField(blank=True, null=True)
    title = models.CharField(max_length=110, blank=True, null=True)
    members_count = models.IntegerField(blank=True, null=True)
    owner_id = models.BigIntegerField(db_index=True)
    conversation_is_registered = models.BooleanField(default=False)

    smart_mode = models.BooleanField(default=False)

    interval_mode = models.BooleanField(default=False)
    interval = models.PositiveIntegerField(blank=True, null=True)
    messages_till_endpoint = models.PositiveIntegerField(blank=True, null=True)  # includes zero

    first_contact = models.DateTimeField(default=timezone.now)
    last_contact = models.DateTimeField(default=timezone.now)


class ChatMessage(models.Model):
    text = models.TextField(blank=True)
    chat_id = models.ForeignKey(
        Chat, on_delete=models.CASCADE)
    from_user_id = models.BigIntegerField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.text)


class UserMessage(models.Model):
    text = models.TextField(blank=True)
    from_id = models.BigIntegerField()
    time = models.DateTimeField(default=timezone.now)


class IntervalPhrase(models.Model):
    id = models.AutoField(primary_key=True)
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    phrase = models.CharField(max_length=4000)




class SmartReply(models.Model):
    id = models.AutoField(primary_key=True)
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    trigger = models.CharField(max_length=100)
    reply = models.CharField(max_length=100)
    last_used = models.DateTimeField(default=five_minutes_ago, blank=True)





class NewPostSetting(models.Model):
    chat_id = models.OneToOneField(
        Chat, on_delete=models.CASCADE, primary_key=True)
    newpost_mode = models.BooleanField(default=False)
    newpost_group_link = models.CharField(max_length=200, blank=True)
    # TODO group address validator
    newpost_group_id = models.BigIntegerField(blank=True, null=True)
    latest_newpost_timestamp = models.BigIntegerField(default=0)


class KickNonMembersSetting(models.Model):
    chat_id = models.OneToOneField(
        Chat, on_delete=models.CASCADE, primary_key=True)
    kick_nonmembers_mode = models.BooleanField(default=False)
    kick_nonmembers_group_link = models.CharField(max_length=200, blank=True)
    # TODO group address validator
    kick_nonmembers_group_id = models.BigIntegerField(blank=True, null=True)


class RandomPostSetting(models.Model):
    chat_id = models.OneToOneField(
        Chat, on_delete=models.CASCADE, primary_key=True)
    random_post_mode = models.BooleanField(default=False)
    random_post_group_link = models.CharField(max_length=200, blank=True, )
    # TODO group address validator
    random_post_group_id = models.BigIntegerField(blank=True, null=True)
