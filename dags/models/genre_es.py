from base import EntityMixinES
from typing import Optional, List


class GenreES(EntityMixinES):
    name: str
    description: Optional[str] = None
