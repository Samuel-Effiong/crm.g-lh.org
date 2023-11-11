from datetime import date

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from users.models import Shepherd

CHOICES = (
    ('prayer_marathon', 'Prayer Marathon'),
    ('bible_reading', 'Bible Reading'),
    ('church_work', 'Church Work'),
    ('evangelism', 'Evangelism'),
    ('prophetic_vision', 'Prophetic Vision'),
    ('bio_data', 'Bio Data'),
    ('shepherd_report', 'Shepherd Report'),
)


class RecentActivityManager(models.Manager):
    def auto_delete_old_activities(self, username):
        all_activities = self.get_queryset().filter(username=username).order_by('date')
        old_activities = all_activities[10:]
        new_activities = all_activities[:10]

        if old_activities:
            for activity in old_activities:
                activity.delete()

        return new_activities


class RecentActivity(models.Model):
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field='username')
    category = models.CharField(max_length=20, choices=CHOICES)
    date = models.DateField(auto_now_add=True)
    details = models.CharField(max_length=100, blank=True, null=True)

    objects = models.Manager()
    custom_objects = RecentActivityManager()

    def __str__(self):
        return f"{self.category} on {self.date}"

    class Meta:
        ordering = ('-date',)
        verbose_name_plural = "Recent Activities"


class BirthdayMessageManager(models.Manager):
    def get_user_birthday_message(self, receiver):
        return self.get_queryset().filter(receiver=receiver)


class BirthdayMessage(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, to_field='username',
                               related_name='birthdaymessage_sender_set')
    receiver = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, to_field='username',
                                 related_name='birthdaymessage_reciever_set')
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    objects = BirthdayMessageManager()

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return f"Happy Birthday Message to {self.sender.username} from {self.receiver.username}"


URGENCY_LEVEL_CHOICES = (
    ('Normal', 'Normal'),
    ('Important', 'Important'),
    ('Critical', 'Critical'),
    ('Emergency', 'Emergency')
)

CATEGORY_CHOICES = (
    ('Suggestion', 'Suggestion'),
    ('Complaint', 'Complaint'),
)


class SuggestionComplaintManager(models.Manager):
    def retrieve_sheep_suggestions_complaints(self, shepherd):
        """Returns the suggestions and complaints that was sent to the sender
        shepherd"""
        if not isinstance(shepherd, Shepherd):
            raise TypeError("Must be a shepherd instance")
        suggestion_complaints = self.get_queryset().filter(receiver=shepherd)

        return suggestion_complaints

    def retrieve_suggestions_complaints_statistics(self):
        # For Chief Shepherd ONLY
        suggestions_complaints = self.get_queryset()

        shepherds = suggestions_complaints.values_list('receiver', flat=True)
        unique_shepherd = set(shepherds)
        receivers_dict = {shepherd: {'suggestions': 0, 'complaints': 0, 'full_name': None,
                                     'unread_message': 0}
                          for shepherd in unique_shepherd}

        for message in suggestions_complaints:
            if message.category == 'Suggestion':
                receivers_dict[message.receiver.id]['suggestions'] += 1

            elif message.category == 'Complaint':
                receivers_dict[message.receiver.id]['complaints'] += 1

            if not message.message_seen:
                receivers_dict[message.receiver.id]['unread_message'] += 1

            full_name = receivers_dict[message.receiver.id]['full_name']
            if full_name is None:
                receivers_dict[message.receiver.id]['full_name'] = message.receiver.name.get_full_name()

        return receivers_dict


class SuggestionComplaintMessage(models.Model):
    """A table to hold suggestions or complaint that is sent to a shepherd"""
    sender = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    receiver = models.ForeignKey(Shepherd, on_delete=models.CASCADE)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    level_of_urgency = models.CharField(max_length=15, choices=URGENCY_LEVEL_CHOICES)
    title = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    date_sent = models.DateTimeField(default=timezone.now)
    message_seen = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = SuggestionComplaintManager()

    def __str__(self):
        return f"{self.category} by {self.sender} on {self.date_sent}"

    class Meta:
        ordering = ('-date_sent',)


NOTIFICATION_MODE_CHOICES = (
    ('Birthday', 'Birthday'),
    ('Suggestion/Complaint', 'Suggestion/Complaint'),
    ('Shepherd Report', 'Shepherd Report'),
)

SENSITIVITY_PERIOD = (
    ('None', 'None'),
    ('1 DAY', '1 DAY')
)

EXPOSURE_LEVEL_CHOICES = (
    ('general', 'general'),
    ('pastoral', 'pastoral'),
    ('all', 'all')
)


class Notification(models.Model):

    # The target for the notification can never be none
    target = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                               related_name='target')
    mode = models.CharField(max_length=50, choices=NOTIFICATION_MODE_CHOICES)
    exposure_level = models.CharField(default='general', max_length=50, choices=EXPOSURE_LEVEL_CHOICES)

    # if target is None, then it means that the notification is addressing
    # multiple people at once
    activator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='activator')

    message = models.CharField(max_length=255, null=True, blank=True)
    time_sensitivity = models.CharField(max_length=15, choices=SENSITIVITY_PERIOD)
    date_activated = models.DateTimeField(default=timezone.now)

    # contains only
    additional_info = models.CharField(max_length=1000, blank=True, null=True)

    # Can only be activated by the target clicking on the notification
    is_activated = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.target} from {self.activator} on {self.mode}"

    class Meta:
        ordering = ('is_activated', )

    def evaluate_additional_info(self):
        """Returns only the primary key of the associated model"""
        if self.mode == 'Shepherd Report':
            try:
                arg = self.additional_info
                arg_dict = eval(arg)
            except TypeError:
                return None
            else:
                return arg_dict['pk']
        else:
            return None
