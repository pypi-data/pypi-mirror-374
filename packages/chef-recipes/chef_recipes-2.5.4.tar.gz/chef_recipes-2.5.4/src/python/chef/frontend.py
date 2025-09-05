import os
from typing import Optional

from loguru import logger

try:
    # < 3.11
    from distutils.sysconfig import get_python_lib
    SITE_PACKAGES_PATH = get_python_lib()
except ImportError:
    # >= 3.12
    import sysconfig
    SITE_PACKAGES_PATH = sysconfig.get_path('purelib')

LOCAL_FRONTEND_SRC = "./src/js/chef/dist"

def get_bundled_frontend_path() -> Optional[str]:
    frontend_root = os.path.join(SITE_PACKAGES_PATH, "src", "js", "chef", "dist")
    logger.info(frontend_root)
    if os.path.isdir(frontend_root):
        return frontend_root


def get_locally_build_frontend_path():
    if not os.path.isdir(LOCAL_FRONTEND_SRC):
        raise FileNotFoundError(f"'{LOCAL_FRONTEND_SRC}', local frontend has to be built first using 'npm run build'")
    return "./src/js/chef/dist"


def get_default_frontend_path() -> str:
    try:
        return get_bundled_frontend_path() or get_locally_build_frontend_path()
    except FileNotFoundError as exc:
        raise Exception(
            f"Built frontend application not found in the bundled together with the python package, "
            f"if you are running chef from sources make sure frontend application is built "
            f"at the expected location: '{LOCAL_FRONTEND_SRC}'"
        ) from exc