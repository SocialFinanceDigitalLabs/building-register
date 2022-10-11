release: python manage.py migrate
web: trap '' SIGTERM; gunicorn buildingregister.wsgi & ./manage.py qcluster & wait -n; kill -SIGTERM -$$; wait
