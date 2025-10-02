release: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py create_admin && python manage.py create_socialapps
web: gunicorn wbs_project.wsgi:application --bind 0.0.0.0:$PORT --log-level debug --timeout 120
