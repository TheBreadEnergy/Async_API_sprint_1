create-migration:
	docker-compose exec django-api python manage.py makemigrations movies

fake-migrations:
	docker-compose exec django-api python manage.py migrate --fake movies 0001_initial

migration:
	docker-compose exec django-api python manage.py migrate

admin:
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=123qwe \
	DJANGO_SUPERUSER_EMAIL=samir@mail.ru \
	docker-compose exec django-api python manage.py createsuperuser --noinput || true

