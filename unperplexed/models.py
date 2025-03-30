from django.db import models

from users.my_models import CustomUser

# Create your models here.

class Worker(models.Model):
    """
    Represents a worker in the system.

    Attributes:
        name (ForeignKey): A reference to the CustomUser model representing the worker's name.
        rating (float): A rating for the worker, default is 0.
        availability_status (bool): Indicates if the worker is available, default is True.
        date_added (DateTimeField): The date and time when the worker was added, automatically set on creation.
    """
    
    WORKER_CATEGORIES = (
        ('construction', 'Construction'),
        ('design', 'Design'),
        ('agriculture', 'Agriculture'),
        ('event_services', 'Event Services')
    ) 
    
    name = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    rating = models.FloatField(default=0)
    availability_status = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, choices=WORKER_CATEGORIES)
    
    class Meta:
        ordering = ('-date_added', )

    def __str__(self) -> str:
        return str(self.name)
    
    
class Skill:
    pass


class Contract(models.Model):
    """Tracks project/contracts workers are booked for

    Args:
        models (_type_): _description_
        
        organization_name (CharField)
        project_title (CharField)
        project_description (TextField)
        start_date (DateField)
        end_date (DateField)
        status (CharField with choices: Pending, In Progress, Completed)
        progress_updates (TextField, optional for artisan's updates)
        budget (DecimalField)

    """
    
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    organization_name = models.ForeignKey('Organization', on_delete=models.CASCADE)
    project_title = models.CharField(max_length=255)
    project_description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'), ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
        ]
    )
    progress_updates = models.TextField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    project_duration = models.PositiveSmallIntegerField(default=0)


class Organization(models.Model):
    """tracks organizations that book workers

    Args:
        models (_type_): _description_
    """
    
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self) -> str:
        return self.name
    
    
class Notification:
    """Tracks notification for workers and organization
    """
    

