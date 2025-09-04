from pydantic import BaseModel


class Config(BaseModel):

    db_url: str = ""
    allow_default_user: bool = False


def get_default_config() -> Config:
    return Config(allow_default_user=True)
