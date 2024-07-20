from importlib import import_module
import logging
from pathlib import Path

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .. import models

admins = list(Path(__file__).parent.glob("*admin.py"))

for item in admins:
    name: str = item.name.replace(".py", "")
    module_prefix: str = ".".join(item.parts[2:-1])
    module: str = f"{module_prefix}.{name}"
    import_module(module)


for name in models.__all__:
    model = getattr(models, name)
    try:admin.site.register(model)
    except AlreadyRegistered as exc:
        logging.warning(exc)
