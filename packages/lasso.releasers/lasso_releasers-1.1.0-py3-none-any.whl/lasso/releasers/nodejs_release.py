"""Node.js release automation."""
import json
import os

from .release import release_publication

SNAPSHOT_TAG_SUFFIX = "-unstable"


def nodejs_get_version(workspace=None):
    """Get the version out of the ``workspace``."""
    workspace = workspace or os.environ.get("GITHUB_WORKSPACE")
    package_path = os.path.join(workspace, "package.json")
    with open(package_path, "r") as package_json_io:
        metadata = json.load(package_json_io)
        return metadata["version"]


def nodejs_upload_assets(repo_name, tag_name, release):
    """Upload Node.js assets.

    This is a no-op since npm knows how to install from a GitHub release itself, so we just let
    the GitHub release happen without any additional assets to upload.
    """
    pass


def main():
    """Entrypoint."""
    release_publication(SNAPSHOT_TAG_SUFFIX, nodejs_get_version, nodejs_upload_assets)


if __name__ == "__main__":
    main()
