# Import sample data through the Data page

From the repository folder, run:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

If you already have an administrator account, skip createsuperuser. Choose your own login credentials. No account or password is created automatically.

1. Open http://127.0.0.1:8000/data/ and sign in using your administrator email and password.
2. Choose `sample_data/dashboard_metrics.json` and click **Import data**.
3. The success message reports added and updated records. A first import adds 288 records across three offices.
4. The table previews the latest 50 stored records. Re-uploading updates matching office/month/level/metric records without duplicating them. Missing rows in a new file are not deleted.

The upload is validated and saved in a single database transaction. Values are saved to MetricRecord rows in the configured database (SQLite locally), not just held in the browser. DataImport stores the filename, uploader, upload time, and added/updated counts. It does not retain the original file or historical versions of edited values.

Administrators can import across offices and create offices named in the file. For an office director, assign the account to an existing office and grant **Can add metric record** in Django admin. That account can import only rows whose office name exactly matches its assigned office. Uploaded office IDs are not trusted as database IDs. Other signed-in users can view their own office records but cannot upload. These permissions use Django's existing permission system; a full application role-management interface is outside this change.

This implements JSON uploads for the supplied demo format. The SRS's CSV upload flow and dashboard charts/filters are still separate work. The JSON upload does not automatically create dashboard visualizations.
