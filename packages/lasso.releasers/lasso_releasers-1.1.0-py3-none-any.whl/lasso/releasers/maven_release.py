"""Maven release automation."""
import fnmatch
import os
import sys

from lxml import etree

from .release import release_publication

SNAPSHOT_TAG_SUFFIX = "SNAPSHOT"


def maven_get_version(workspace=None):
    """Get the maven version out of the ``workspace``."""
    # read current version
    workspace = workspace or os.environ.get("GITHUB_WORKSPACE")
    pom_path = os.path.join(workspace, "pom.xml")
    pom_doc = etree.parse(pom_path)
    r = pom_doc.xpath(
        "/pom:project/pom:version",
        namespaces={"pom": "http://maven.apache.org/POM/4.0.0"},
    )
    version = r[0].text
    print(f"Yo yo maven gets version {version} from the pom", file=sys.stderr)
    return version


def maven_upload_assets(repo_name, tag_name, release):
    """Upload packages produced by maven."""
    print(f"Yo yo maven upload assets for {repo_name} and tag {tag_name}", file=sys.stderr)
    # upload assets
    assets = ["*-bin.tar.gz", "*-bin.zip", "*.jar"]
    for dirname, _subdirs, files in os.walk(os.environ.get("GITHUB_WORKSPACE")):
        if dirname.endswith("target"):
            for extension in assets:
                for filename in fnmatch.filter(files, extension):
                    with open(os.path.join(dirname, filename), "rb") as f_asset:
                        release.upload_asset("application/tar+gzip", filename, f_asset)


def main():
    """Entrypoint."""
    release_publication(SNAPSHOT_TAG_SUFFIX, maven_get_version, maven_upload_assets)


if __name__ == "__main__":
    main()
