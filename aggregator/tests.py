import copy
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import DataUploadForm
from .imports import import_records
from .models import DataImport, MetricRecord, Office, User


class DataImportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin', 'admin@example.test', 'test-password')
        cls.office = Office.objects.create(name='Retriever Essentials')
        cls.director = User.objects.create_user('director', 'director@example.test', 'test-password', office=cls.office)
        cls.director.user_permissions.add(Permission.objects.get(codename='add_metricrecord'))
        cls.payload = json.loads((Path(settings.BASE_DIR) / 'sample_data' / 'dashboard_metrics.json').read_text(encoding='utf-8-sig'))

    def upload(self, payload=None):
        return SimpleUploadedFile('metrics.json', json.dumps(payload or self.payload).encode(), content_type='application/json')

    def test_full_sample_import_and_repeat(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('data'), {'json_file': self.upload()}, follow=True)
        self.assertContains(response, '288 records added')
        self.assertEqual(MetricRecord.objects.count(), 288)
        self.assertEqual(Office.objects.count(), 3)
        response = self.client.post(reverse('data'), {'json_file': self.upload()}, follow=True)
        self.assertContains(response, '288 existing records updated')
        self.assertEqual(MetricRecord.objects.count(), 288)
        self.assertEqual(DataImport.objects.count(), 2)

    def test_invalid_last_record_leaves_database_unchanged(self):
        payload = copy.deepcopy(self.payload)
        payload['records'][-1]['value'] = -1
        self.client.force_login(self.admin)
        response = self.client.post(reverse('data'), {'json_file': self.upload(payload)})
        self.assertContains(response, 'Record 288')
        self.assertFalse(MetricRecord.objects.exists())
        self.assertFalse(DataImport.objects.exists())

    def test_duplicate_and_malformed_json(self):
        payload = copy.deepcopy(self.payload)
        payload['records'].append(payload['records'][0])
        form = DataUploadForm(files={'json_file': self.upload(payload)})
        self.assertFalse(form.is_valid())
        self.assertIn('duplicate', str(form.errors))
        form = DataUploadForm(files={'json_file': SimpleUploadedFile('bad.json', b'{')})
        self.assertFalse(form.is_valid())

    def test_director_cannot_import_other_offices(self):
        self.client.force_login(self.director)
        response = self.client.post(reverse('data'), {'json_file': self.upload()})
        self.assertContains(response, 'only import data for your assigned office')
        self.assertFalse(MetricRecord.objects.exists())
        self.assertFalse(DataImport.objects.exists())

    def test_director_import_and_staff_visibility(self):
        payload = copy.deepcopy(self.payload)
        payload['records'] = [r for r in payload['records'] if r['office_name'] == self.office.name]
        self.client.force_login(self.director)
        self.client.post(reverse('data'), {'json_file': self.upload(payload)})
        self.assertEqual(MetricRecord.objects.count(), 96)
        # Import other offices as admin, then verify the office boundary on GET.
        form = DataUploadForm(files={'json_file': self.upload()})
        self.assertTrue(form.is_valid())
        import_records(form.records, self.admin, 'all.json')
        viewer = User.objects.create_user('viewer', 'viewer@example.test', 'test-password', office=self.office)
        self.client.force_login(viewer)
        response = self.client.get(reverse('data'))
        self.assertEqual(response.context['record_count'], 96)
        self.assertTrue(all(r.office_id == self.office.pk for r in response.context['records']))
        self.assertEqual(self.client.post(reverse('data'), {'json_file': self.upload()}).status_code, 403)

    def test_anonymous_cannot_upload_or_see_data(self):
        response = self.client.get(reverse('data'))
        self.assertContains(response, 'Sign in')
        self.assertEqual(response.context['record_count'], 0)
        self.assertEqual(self.client.post(reverse('data'), {'json_file': self.upload()}).status_code, 403)

    def test_zero_decimals_and_bom_are_supported(self):
        content = b'\xef\xbb\xbf' + json.dumps(self.payload).encode()
        form = DataUploadForm(files={'json_file': SimpleUploadedFile('demo.json', content)})
        self.assertTrue(form.is_valid(), form.errors)
        batch = import_records(form.records, self.admin, 'demo.json')
        self.assertEqual(batch.created_count, 288)
        self.assertTrue(MetricRecord.objects.filter(value=0).exists())
        self.assertTrue(MetricRecord.objects.filter(metric='food_distributed_lb', value__gt=0).exists())

    def test_inconsistent_units_roll_back(self):
        form = DataUploadForm(files={'json_file': self.upload()})
        self.assertTrue(form.is_valid())
        import_records(form.records, self.admin, 'first.json')
        changed = dict(form.records[0], unit='wrong-unit')
        with self.assertRaises(ValidationError):
            import_records([changed], self.admin, 'bad.json')
        self.assertEqual(DataImport.objects.count(), 1)
