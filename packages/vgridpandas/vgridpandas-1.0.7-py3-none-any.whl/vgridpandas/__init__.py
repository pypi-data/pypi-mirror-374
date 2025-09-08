__author__ = """Thang Quach"""
__email__ = "quachdongthang@gmail.com"

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("vgridpandas")
except PackageNotFoundError:
    # package is not installed
    pass
