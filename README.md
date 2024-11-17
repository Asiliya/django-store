git clone https://github.com/Asiliya/django-store
docker compose up
docker-compose run --rm web sh -c 'python manage.py createsuperuser'