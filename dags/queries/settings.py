import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="")


class DatabaseSettings(EnvironmentBaseSettings):
    database_schema = Field("content", alias="DB_SCHEMA", env="DB_SCHEMA")
    database_movie_table = Field(
        "film_work", alias="DB_MOVIE_TABLE", env="DB_MOVIE_TABLE"
    )
    database_genre_table = Field("genre", alias="DB_GENRE_TABLE", env="DB_GENRE_TABLE")
    database_person_table = Field(
        "person", alias="DB_PERSON_TABLE", env="DB_PERSON_TABLE"
    )
    database_movie_genre_m2m_table = Field(
        "genre_film_work",
        alias="DB_MOVIE_GENRE_M2M_TABLE",
        env="DB_MOVIE_GENRE_M2M_TABLE",
    )
    database_movie_person_m2m_table = Field(
        "person_film_work", alias="DB_MOVIE_GENRE_M2M_TABLE"
    )
    movie_table = Field(f"{database_schema}.{database_movie_table}")
    genre_table = Field(f"{database_schema}.{database_genre_table}")
    person_table = Field(f"{database_schema}.{database_person_table}")
    movie_genre_table = Field(f"{database_schema}.{database_movie_genre_m2m_table}")
    movie_person_table = Field(f"{database_schema}.{database_movie_person_m2m_table}")


DB_SETTINGS = DatabaseSettings()
