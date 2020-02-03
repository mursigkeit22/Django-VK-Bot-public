from django.db import models
from django.utils import timezone


class ChatConversation(models.Model):
    peer_id = models.BigIntegerField(primary_key=True)
    local_id = models.BigIntegerField()
    type = models.CharField(max_length=20)
    owner_id = models.BigIntegerField()
    members_count = models.IntegerField(blank=True, null=True)
    conversation_is_registered = models.BooleanField(default=False)
    kick_nonmembers_mode = models.BooleanField(default=False)
    interval_mode = models.BooleanField(default=False)
    random_post_mode = models.BooleanField(default=False)
    newpost_mode = models.BooleanField(default=False)
    first_contact = models.DateTimeField(default=timezone.now)
    last_contact = models.DateTimeField(default=timezone.now)

    # TODO ссылку на таблицу с сообщениями.

    def __str__(self):
        return str(self.peer_id)


class UserConversation(models.Model):  # TODO: добавить юзернейм, а то по цифрам неудобно # а если юзер сменит имя?
    peer_name = models.CharField(blank=True, max_length=30)
    peer_id = models.BigIntegerField(primary_key=True)
    local_id = models.BigIntegerField()
    type = models.CharField(max_length=20)
    number_of_messages = models.IntegerField(blank=True, null=True)
    first_contact = models.DateTimeField(default=timezone.now)
    last_contact = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.peer_id)


class ChatMessage(models.Model):
    text = models.TextField(blank=True)
    peer_id = models.ForeignKey(
        ChatConversation, on_delete=models.CASCADE)
    message_id = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=30)
    user_id = models.BigIntegerField()
    type = models.CharField(max_length=20,
                            blank=True)  # text, служебное, фото? а если несколько вложений? просто атачментс?

    def __str__(self):  # можно сделать так, чтобы в строковом представлении был еще peer_id?
        return str(self.text)


class UserMessage(models.Model):
    text = models.TextField(blank=True)
    peer_id = models.ForeignKey(
        UserConversation, on_delete=models.CASCADE)
    message_id = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=30)
    user_id = models.BigIntegerField()
    type = models.CharField(max_length=20,
                            blank=True)

    def __str__(self):
        return str(self.text)


class ChatSetting(models.Model):
    peer_id = models.OneToOneField(
        ChatConversation, on_delete=models.CASCADE, primary_key=True)
    remove_group = models.CharField(max_length=30, blank=True, null=True)
    random_post_group = models.CharField(max_length=30, blank=True, null=True)
    interval = models.IntegerField(blank=True, null=True)
    messages_till_endpoint = models.IntegerField(blank=True, null=True)
    newpost_group = models.CharField(max_length=30, blank=True, null=True)
    latest_newpost_timestamp = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.peer_id)


class IntervalPhrase(models.Model):

    id = models.AutoField(primary_key=True)
    peer_id = models.ForeignKey(ChatConversation, on_delete=models.CASCADE)
    phrase = models.CharField(max_length=4000)

    def __str__(self):
        return str(self.id) + ', ' + str(self.peer_id) + ', ' + str(self.phrase)
