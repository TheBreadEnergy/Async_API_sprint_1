admin:
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=PpAaSs!123 \
	DJANGO_SUPERUSER_EMAIL=samir@mail.ru \
	docker-compose exec django-api python manage.py createsuperuser --noinput || true


run-dev:
	docker-compose -f docker-compose-dev.yaml up


stop-dev:
	docker-compose -f docker-compose-dev.yaml down
