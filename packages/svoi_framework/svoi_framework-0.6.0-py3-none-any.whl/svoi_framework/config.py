import yaml

from pathlib import Path
from pydantic import BaseModel


def read_config[T: BaseModel](model: type[T], file_path: Path) -> T:
    with open(file_path, "r") as file:
        raw_data = yaml.safe_load(file)
        return model.model_validate(raw_data)
