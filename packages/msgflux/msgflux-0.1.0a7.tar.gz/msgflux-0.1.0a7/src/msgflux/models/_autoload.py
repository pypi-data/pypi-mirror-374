import importlib
import pkgutil
import pathlib

_providers_loaded = False

def autoload_providers():
    global _providers_loaded
    if _providers_loaded:
        return

    from msgflux.models import providers
    package_path = pathlib.Path(providers.__file__).parent

    for module_info in pkgutil.iter_modules([str(package_path)]):
        if module_info.name.startswith("_"):
            continue
        importlib.import_module(f"msgflux.models.providers.{module_info.name}")

    _providers_loaded = True
