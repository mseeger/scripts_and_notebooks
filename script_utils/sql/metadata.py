from sqlalchemy import MetaData, Engine


class DatabaseMetaData:
    """
    Represents metadata for the database associated with an engine passed at
    construction.
    """
    def __init__(self, engine: Engine):
        self._metadata = MetaData()
        self._metadata.reflect(engine)

    @property
    def metadata(self) -> MetaData:
        return self._metadata

    def table_names(self) -> list[str]:
        return list(self._metadata.tables.keys())
