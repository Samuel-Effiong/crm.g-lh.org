from django.db import models
from django.contrib.auth import get_user_model
from project_management.models import Department


# Create your models here.

STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
    ('Under Maintenance', 'Under Maintenance'),
    ('Disposed', 'Disposed'),
]


CONDITION_CHOICES = [
    ('Excellent', 'Excellent'),
    ('Good', 'Good'),
    ('Bad But In Use', 'Bad But In Use'),
    ('Bad But Can Be Fixed', 'Bad But Can Be Fixed'),
    ('Bad and Out of Use', 'Bad and Out of Use'),
    ('Very Bad', 'Very Bad')
]


REQUEST_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
    ('Completed', 'Completed'),
]


LOCATION_CHOICES = [
    ('Afaha-Ube House', 'Afaha-Ube House'),
    ('Bethel House', 'Bethel House'),
    ('Commonwealth House', 'Commonwealth House'),
    ('Shelter-Afrique Farmhouse', 'Shelter-Afrique Farmhouse'),
    ('The 3rd Floor', 'The 3rd Floor'),
    ('The Manse', 'The Manse'),
    ('UdoAbasi House', 'UdoAbasi House'),
    ('Udoette House', 'Udoette House'),
    ('Udomita Farmhouse', 'Udomita Farmhouse'),
]

SOURCE_OF_ITEM_CHOICES = [
    ('Co-ownership', 'Co-ownership'),
    ('Gift|Donation', 'Gift|Donation'),
    ('Purchase', 'Purchase'),
]


class AssetFile(models.Model):
    FILE_CHOICES = (
        ('image', 'img'),
        ('video', 'video')
    )
    name = models.CharField(max_length=1000)
    type = models.CharField(max_length=20, choices=FILE_CHOICES)
    size = models.IntegerField(null=True, blank=True)


class Asset(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField('Description|Configuration')
    category = models.ForeignKey('AssetCategory', on_delete=models.CASCADE)
    purchase_date = models.DateField('Date of Acquisition')

    location = models.CharField(max_length=100)
    condition = models.CharField(
        max_length=50, choices=CONDITION_CHOICES,
        help_text="These choices represent the condition of assets, allowing for clear categorization."
    )
    source_of_item = models.CharField(max_length=50, choices=SOURCE_OF_ITEM_CHOICES)
    files = models.ManyToManyField(AssetFile, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Active',
        help_text="These choices can be used to indicate the current status of assets or requests."
    )

    def __str__(self):
        return self.name
    
    # class Meta:
    #     ordering = ('purchased_date',)


class AssetCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Asset Categories'

    def __str__(self):
        return self.name


class MaintenanceSchedule(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    maintenance_type = models.CharField(max_length=100)
    service_provider = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    def __str__(self):
        return f"{self.maintenance_type} - {self.asset.name}"


class TreasuryRequest(models.Model):
    requested_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=REQUEST_STATUS_CHOICES, default='Pending',
        help_text="These choices are specifically for the status of resource requests."
    )
    reason = models.TextField()
    approved_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    approved_date = models.DateField(null=True, blank=True)
    new_location = models.CharField(max_length=1000, choices=LOCATION_CHOICES, default="")
    preferred_date = models.DateField(null=True, blank=True, help_text="Deadline for the request")

    def __str__(self):
        return f"Request {self.id} for {self.asset.name}"


class Audit(models.Model):
    audit_id = models.CharField(max_length=20, unique=True)
    audit_date = models.DateField(auto_now_add=True)
    auditor = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Audit {self.audit_id} on {self.audit_date}"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('Acquisition', 'Acquisition'),
        ('Disposal', 'Disposal'),
        ('Transfer', 'Transfer'),
    ]
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateField()
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.asset.name} on {self.transaction_date}"


class Report(models.Model):
    report_type = models.CharField(max_length=50)
    generated_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    generated_date = models.DateField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.report_type} generated by {self.generated_by}"
