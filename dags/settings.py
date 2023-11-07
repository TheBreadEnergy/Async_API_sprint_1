from pydantic import Field
from queries.settings import EnvironmentBaseSettings


class ApplicationSettings(EnvironmentBaseSettings):
    postgres_connection_id: str = Field(
        "postgres",
        alias="POSTGRES_CONNECTION_ID",
        env="POSTGRES_CONNECTION_ID",
    )
    options: str = Field(
        "-c search_path=public,content", alias="OPTIONS", env="OPTIONS"
    )
    batch_size: int = Field(100, alias="BATCH_SIZE", env="BATCH_SIZE")
    movie_state_key: str = Field(
        "movie_last_updated", alias="MOVIE_STATE_KEY", env="MOVIE_STATE_KEY"
    )
    genre_state_key: str = Field(
        "genre_last_updated", alias="GENRE_STATE_KEY", env="GENRE_STATE_KEY"
    )
    person_state_key: str = Field(
        "person_last_updated", alias="PERSON_STATE_KEY", env="PERSON_STATE_KEY"
    )
    es_movies_index: str = Field("movies", alias="MOVIE_INDEX", env="MOVIE_INDEX")
    es_genre_index: str = Field("genres", alias="GENRE_INDEX", env="GENRE_INDEX")
    es_person_index: str = Field("persons", alias="PERSON_INDEX", env="PERSON_INDEX")
    movie_dag: str = Field("Movie_ETL", alias="MOVIE_DAG", env="MOVIE_DAG")
    genre_dag: str = Field("Genre_ETL", alias="GENRE_DAG", env="GENRE_DAG")
    person_dag: str = Field("Person_ETL", alias="PERSON_DAG", env="PERSON_DAG")
    interval: int = Field(1, alias="ETL_INTERVAL", env="ETL_INTERVAL")


class ElasticsearchDSN(EnvironmentBaseSettings):
    host: str = Field("elastic", alias="ELASTICSEARCH_HOST", env="ELASTICSEARCH_HOST")
    port: int = Field(9200, alias="ELASTICSEARCH_PORT", env="ELASTICSEARCH_PORT")


APP_SETTINGS = ApplicationSettings()
ES_DSN = ElasticsearchDSN()
