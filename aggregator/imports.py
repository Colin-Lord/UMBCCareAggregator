from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import DataImport, MetricRecord, Office


def can_upload(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm('aggregator.add_metricrecord'))


@transaction.atomic
def import_records(records, user, filename):
    if not can_upload(user):
        raise PermissionDenied
    # Resolve ownership using the account's office, never uploaded IDs.
    if not user.is_superuser:
        if not user.office_id or any(row['office_name'] != user.office.name for row in records):
            raise ValidationError('You can only import data for your assigned office. Ask an administrator to import multiple offices.')
    for row in records:
        if MetricRecord.objects.filter(metric=row['metric']).exclude(unit=row['unit']).exists():
            raise ValidationError(f"Metric {row['metric']} already uses a different unit. No records were imported.")
    batch = DataImport.objects.create(filename=filename[:255], uploaded_by=user)
    offices = {}
    for row in records:
        name = row['office_name']
        if name not in offices:
            offices[name] = Office.objects.get_or_create(name=name)[0] if user.is_superuser else user.office
        _, created = MetricRecord.objects.update_or_create(
            office=offices[name], time_period=row['time_period'],
            student_level=row['student_level'], metric=row['metric'],
            defaults={field: row[field] for field in ('period_end', 'value', 'unit', 'is_demo')} | {'last_import': batch},
        )
        if created:
            batch.created_count += 1
        else:
            batch.updated_count += 1
    batch.save(update_fields=['created_count', 'updated_count'])
    return batch
