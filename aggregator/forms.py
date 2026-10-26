import calendar
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from django import forms


class DataUploadForm(forms.Form):
    json_file = forms.FileField(
        label='JSON data file',
        widget=forms.ClearableFileInput(attrs={
            'accept': '.json,application/json', 'class': 'form-control',
        }),
        help_text='Choose dashboard_metrics.json from the sample_data folder. Maximum 2 MB.',
    )

    def clean_json_file(self):
        upload = self.cleaned_data['json_file']
        if not upload.name.lower().endswith('.json'):
            raise forms.ValidationError('Choose a .json file.')
        if upload.size > 2 * 1024 * 1024:
            raise forms.ValidationError('The file must be 2 MB or smaller.')
        try:
            payload = json.loads(upload.read().decode('utf-8-sig'), parse_float=Decimal)
        except (ValueError, UnicodeDecodeError, RecursionError):
            raise forms.ValidationError('This file is not valid UTF-8 JSON.')
        if not isinstance(payload, dict) or type(payload.get('schema_version')) is not int or payload['schema_version'] != 1:
            raise forms.ValidationError('Expected a JSON object with schema_version set to 1.')
        records = payload.get('records')
        if not isinstance(records, list) or not 1 <= len(records) <= 10000:
            raise forms.ValidationError('Include between 1 and 10,000 records in the records list.')
        cleaned = []
        keys = set()
        office_names = {}
        metric_units = {}
        for number, row in enumerate(records, 1):
            try:
                if not isinstance(row, dict):
                    raise ValueError('each record must be an object')
                for field, limit in [('office_id', 100), ('office_name', 255),
                                     ('metric', 100), ('unit', 30)]:
                    if not isinstance(row.get(field), str) or not row[field].strip() or len(row[field]) > limit:
                        raise ValueError(f'{field} must be nonempty text up to {limit} characters')
                if not re.fullmatch(r'[a-z][a-z0-9_]*', row['metric']):
                    raise ValueError('metric must use lowercase letters, numbers, and underscores')
                start = date.fromisoformat(row['time_period'])
                end = date.fromisoformat(row['period_end'])
                if start.day != 1 or end != date(start.year, start.month, calendar.monthrange(start.year, start.month)[1]):
                    raise ValueError('time_period and period_end must describe a complete calendar month')
                if row.get('student_level') not in ('undergraduate', 'graduate'):
                    raise ValueError('student_level must be undergraduate or graduate')
                if type(row.get('is_demo')) is not bool:
                    raise ValueError('is_demo must be true or false')
                if isinstance(row.get('value'), bool) or not isinstance(row.get('value'), (int, Decimal)):
                    raise ValueError('value must be a JSON number')
                value = Decimal(row['value'])
                if not value.is_finite() or value < 0 or value >= Decimal('1000000000000') or value != value.quantize(Decimal('0.01')):
                    raise ValueError('value must be nonnegative, below one trillion, with at most 2 decimal places')
                name = row['office_name'].strip()
                slug = row['office_id'].strip()
                if slug in office_names and office_names[slug] != name:
                    raise ValueError('one office_id cannot have multiple names')
                if any(other != slug and other_name == name for other, other_name in office_names.items()):
                    raise ValueError('different office IDs cannot share a name')
                office_names[slug] = name
                metric = row['metric']
                unit = row['unit'].strip()
                if metric in metric_units and metric_units[metric] != unit:
                    raise ValueError('one metric cannot have multiple units')
                metric_units[metric] = unit
                key = (name, start, row['student_level'], metric)
                if key in keys:
                    raise ValueError('duplicate office, month, student level, and metric')
                keys.add(key)
                cleaned.append(dict(office_name=name, time_period=start, period_end=end,
                                    student_level=row['student_level'], metric=metric,
                                    value=value, unit=unit, is_demo=row['is_demo']))
            except (KeyError, TypeError, ValueError, InvalidOperation) as error:
                raise forms.ValidationError(f'Record {number}: {error}.')
        self.records = cleaned
        return upload
