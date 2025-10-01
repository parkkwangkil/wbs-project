release: python manage.py collectstatic --noinput && python manage.py migrate && python create_admin.py
web: gunicorn wbs_project.wsgi:application --bind 0.0.0.0:$PORT
