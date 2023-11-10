from typing import Optional

from models.base import EntityMixinES


class GenreES(EntityMixinES):
    title: str
    description: Optional[str] = None
