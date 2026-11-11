from django.contrib.auth.models import AbstractUser
from django.db import models

class Office(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser): #custom user model setup to sign in with email
    email = models.EmailField(unique=True)
    office = models.ForeignKey(
        Office,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']


class CSVFile(models.Model):
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    #foreign keys
    office = models.ForeignKey(
        Office,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.filename

class DataRecord(models.Model):
    timeframe = models.CharField(max_length=255) #should be formatted like YYYY-MM-DD (we may change later)

    #foreign keys
    csv_file = models.ForeignKey(
        CSVFile,
        on_delete=models.CASCADE,
        related_name='data_records'
    )

    def __str__(self):
        return f"DataRecord for {self.csv_file.filename}"

class Metric(models.Model):
    name = models.CharField(max_length=255, unique=True)

    #instead of using a junction table, django has built in many to many relationships
    offices = models.ManyToManyField(
        'Office',
        related_name='metrics',
        blank=True,
    )

    def __str__(self):
        return self.name

class MetricValue(models.Model): # i changed the name from what was on our ER diagram to be clearer
    value = models.FloatField()

    data_record = models.ForeignKey(
        DataRecord,
        on_delete=models.CASCADE,
        related_name='values'
    )

    metric = models.ForeignKey(
        Metric,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.metric.name}: {self.value}"