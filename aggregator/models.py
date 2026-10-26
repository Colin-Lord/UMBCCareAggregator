from django.contrib.auth.models import AbstractUser
from django.db import models

class Office(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    office = models.ForeignKey(
        Office,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']


class DataImport(models.Model):
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)


class MetricRecord(models.Model):
    office = models.ForeignKey(Office, on_delete=models.PROTECT)
    time_period = models.DateField()
    period_end = models.DateField()
    student_level = models.CharField(max_length=13, choices=[
        ('undergraduate', 'Undergraduate'), ('graduate', 'Graduate'),
    ])
    metric = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=14, decimal_places=2)
    unit = models.CharField(max_length=30)
    is_demo = models.BooleanField(default=True)
    last_import = models.ForeignKey(DataImport, on_delete=models.PROTECT)

    class Meta:
        ordering = ['-time_period', 'office__name', 'metric', 'student_level']
        constraints = [models.UniqueConstraint(
            fields=['office', 'time_period', 'student_level', 'metric'],
            name='unique_office_month_level_metric',
        )]
