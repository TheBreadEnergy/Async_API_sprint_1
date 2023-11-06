from django.urls import include, path
from movies.api.v1.views import MoviesApi
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("movies", MoviesApi)

urlpatterns = [path("", include(router.urls))]
