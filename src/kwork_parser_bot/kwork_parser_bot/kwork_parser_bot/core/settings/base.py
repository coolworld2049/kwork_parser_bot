import os
import pathlib

from dotenv import load_dotenv, find_dotenv
from pydantic import BaseSettings


class BaseAppSettings(BaseSettings):
    pkg_path = pathlib.Path(__file__).parent.parent.parent
    project_path = pathlib.Path(__file__).parent.parent.parent.parent.parent
    load_dotenv(find_dotenv(f"{project_path}/.env"))
    stage_dotenv = find_dotenv(f'{project_path}/.env.{os.getenv("STAGE", "dev")}')
    load_dotenv(stage_dotenv, override=True) if stage_dotenv else None
