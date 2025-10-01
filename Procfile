release: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py create_admin && python manage.py loaddata data_backup.json
web: gunicorn wbs_project.wsgi:application --bind 0.0.0.0:$PORT
