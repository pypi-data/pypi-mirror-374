# encoding: utf-8
"""Python release automation."""
import glob
import logging
import os

from ._python_version import getversion
from .release import release_publication

_logger = logging.getLogger(__name__)

SNAPSHOT_TAG_SUFFIX = "-dev"


def python_get_version(workspace=None):
    """Get a version from the given ``workspace``."""
    return getversion(workspace)


def python_upload_assets(repo_name, tag_name, release):
    """Upload packages produced by python setup.py."""
    package_pattern = os.path.join(os.environ.get("GITHUB_WORKSPACE"), "dist", "*")
    packages = glob.glob(package_pattern)
    for package in packages:
        with open(package, "rb") as f_asset:
            asset_filename = os.path.basename(package)
            _logger.info(f"Upload asset file {asset_filename}")
            release.upload_asset("application/zip", asset_filename, f_asset)


def main():
    """Main entrypoint."""
    release_publication(SNAPSHOT_TAG_SUFFIX, python_get_version, python_upload_assets)


if __name__ == "__main__":
    main()
