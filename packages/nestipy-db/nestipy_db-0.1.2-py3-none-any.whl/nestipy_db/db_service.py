from functools import lru_cache
from typing import Annotated

from edgy import Database, Registry
from nestipy.common import Injectable
from nestipy.ioc import Inject

from .db_builder import DbConfig, DB_CONFIG


@Injectable()
class DbService:
    _config: Annotated[DbConfig, Inject(DB_CONFIG)]
    db: Database
    registry: Registry

    @lru_cache()
    def get_connection(self):
        self.db = Database(self._config.url)
        self.registry = Registry(database=self.db)
        return self.db, self.registry
