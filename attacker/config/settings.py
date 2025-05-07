# settings.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # C2 server address
    c2_server: str

# TODO fix this file
settings = Settings(c2_server='http://0.0.0.0:8888')