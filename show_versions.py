import sys
from platform import python_version, python_build


def show_versions(deps):
    import psutil

    print(f"python version: {python_version()}")
    print(f"python build: {python_build()}")
    print(f"python path: {sys.executable}")

    print(f"Memory: {psutil.virtual_memory()}")
    print(f"Physical Core: {psutil.cpu_count(logical=False)}")
    print(f"Logical Core: {psutil.cpu_count(logical=True)}")

    for dep_name in deps:
        print(f"{dep_name}: {_get_dependency_version(dep_name)}")


def _get_dependency_version(dep_name: str) -> str:
    # note: we import 'importlib' here as a significiant optimisation for initial import
    import importlib
    import importlib.metadata

    try:
        module = importlib.import_module(dep_name)
    except ImportError:
        return "<not installed>"

    if hasattr(module, "__version__"):
        module_version = module.__version__
    else:
        module_version = importlib.metadata.version(dep_name)

    return module_version
