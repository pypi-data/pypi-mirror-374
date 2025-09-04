import platform

# need these functions exposed so apps can use them when running. should support on each platform
if platform.system().casefold() == "windows":
    from .windows import is_bundled, get_entrypoint_dirpath  # noqa: F401
else:
    raise RuntimeError("Platform not supported")


__version__ = "1.1.4"
