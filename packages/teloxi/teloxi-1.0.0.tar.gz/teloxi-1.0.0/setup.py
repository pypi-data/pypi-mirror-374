from setuptools import setup, find_packages
from pathlib import Path
import re

def get_version():
    version_file = Path("teloxi/version.py")
    content = version_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\'](.+?)["\']', content)
    if match:
        return match.group(1)
    raise RuntimeError("Cannot find __version__ in teloxi/version.py")

setup(
    name="teloxi",
    version=get_version(),
    packages=find_packages(),
)