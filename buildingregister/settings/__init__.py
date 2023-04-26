from dotenv import load_dotenv

load_dotenv()

import os
from pathlib import Path

from split_settings.tools import include, optional

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV = os.environ.get("DJANGO_ENV") or "development"
include(
    f"{ENV}/environment.py",
    optional(f"{ENV}/localsettings.py"),
)
