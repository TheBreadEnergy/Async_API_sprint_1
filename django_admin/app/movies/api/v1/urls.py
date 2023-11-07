from django.urls import path, include
from rest_framework.routers import DefaultRouter

from movies.api.v1 import views
from movies.api.v1.views import MoviesApi

# urlpatterns = [path("movies/", MoviesListApi.as_view())]

router = DefaultRouter()
router.register("movies", MoviesApi)

urlpatterns = [path("", include(router.urls))]