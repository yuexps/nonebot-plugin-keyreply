from pydantic import BaseModel
from pathlib import Path


class Config(BaseModel):
    """Plugin Config Here"""
    keyreply_data_path: Path = Path("data/keyreply/rules.json")
