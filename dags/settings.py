from pydantic import Field

from queries.settings import EnvironmentBaseSettings


class ApplicationSettings(EnvironmentBaseSettings):
    postgres_connection_id: str = Field(
        "postgres_connection",
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
    es_movies_index: str = Field("movies", alias="MOVIE_INDEX", env="MOVIE_INDEX")
    movie_dag: str = Field("Movie_ETL", alias="MOVIE_DAG", env="MOVIE_DAG")
    interval: int = Field(1, alias="ETL_INTERVAL", env="ETL_INTERVAL")


class ElasticsearchDSN(EnvironmentBaseSettings):
    host: str = Field(..., alias="ELASTICSEARCH_HOST", env="ELASTICSEARCH_HOST")
    port: str = Field(..., alias="ELASTICSEARCH_PORT", env="ELASTICSEARCH_PORT")


APP_SETTINGS = ApplicationSettings()
ES_DSN = ElasticsearchDSN()
