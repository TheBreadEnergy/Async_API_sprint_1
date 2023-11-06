from typing import Optional

from models.base import EntityMixinES


class GenreES(EntityMixinES):
    name: str
    description: Optional[str] = None
