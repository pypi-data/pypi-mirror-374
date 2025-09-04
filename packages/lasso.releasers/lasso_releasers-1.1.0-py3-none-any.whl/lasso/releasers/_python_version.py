# encoding: utf-8
"""🐱 PDS GitHub Utilities: Python Version determination."""
import logging
import os
import re
import subprocess
import sys

import packaging.version


_logger = logging.getLogger(__name__)
_detectives = set()


# Classes
# -------


class NoVersionDetectedError(ValueError):
    """😦 Raised when we cannot detect a version from a Python workspace."""


class VersionDetective(object):
    """🕵️‍♀️ Abstract detective for a version of a Python package given its source code.

    You can define your own classes by deriving from this class and implementing the ``detect``
    method. This package comes with several implmentations, and you can register your own by calling
    ``registerdetective``.
    """

    def __init__(self, workspace: str):
        """Initialize this detective.

        It works by saving the given workspace (a path to a directory as a string)
        into the instance of this object.
        """
        self.workspace = workspace

    def findfile(self, fn: str):
        """Utility method: Find the file named ``fn`` in the workspace and return its path.

        Return None if it's not found. Handy for subclasses.
        """
        path = os.path.join(self.workspace, fn)
        return path if os.path.isfile(path) else None

    def detect(self):
        """Detect the version of the Python package in the source code ``workspace`` and return it.

        Return None if we can't figure it out.
        """
        raise NotImplementedError("Subclasses must implement ``VersionDetective.detect``")


class VersioneerDetective(VersionDetective):
    """Detective that uses Python Versioneer to tell what version we have."""

    def detect(self):
        """Detect version."""
        if not sys.executable:
            _logger.debug("🤷‍♂️ Cannot tell what my own Python executable is, so not bothering with versioneer")
            return None
        setupfile = self.findfile("setup.py")
        if not setupfile:
            _logger.debug("🤷‍♀️ No setup.py file, so cannot call versioneer command on it")
            return None
        expr = re.compile(r"^Version: (.+)$")
        try:
            completion = subprocess.run(
                [sys.executable, setupfile, "version"],
                check=True,
                cwd=self.workspace,
                encoding="utf-8",
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                text=True,
            )
            for line in completion.stdout.split("\n"):
                match = expr.match(line)
                if match:
                    return match.group(1).strip()
        except subprocess.CalledProcessError as ex:
            _logger.debug(
                "🚳 Could not execute ``version`` command on ``setup.py``, rc=%d",
                ex.returncode,
            )
        return None


class TextFileDetective(VersionDetective):
    """Detective that looks for a ``version.txt`` file of some kind for a version indication."""

    @classmethod
    def locate_file(cls, root_dir):
        """Locate the version file."""
        src_dir = os.path.join(root_dir, "src")
        if not os.path.isdir(src_dir):
            raise ValueError("Unable to locate ./src directory in workspace.")

        version_file = None
        for dirpath, _dirnames, filenames in os.walk(src_dir):
            for fn in filenames:
                if fn.lower() == "version.txt":
                    version_file = os.path.join(dirpath, fn)
                    _logger.debug("🪄 Found a version.txt in %s", version_file)
                    break

        return version_file

    def detect(self):
        """Detect the version."""
        version_file = self.locate_file(self.workspace)
        if version_file is not None:
            with open(version_file, "r", encoding="utf-8") as inp:
                return inp.read().strip()
        else:
            return None


class ModuleInitDetective(VersionDetective):
    """Detective that parses ``__init__.py`` files for a version definition.

    This will use the first one matched; this is typically the highest level one in the package,
    which is what you want.
    """

    def detect(self):
        """Detect the version."""
        expr = re.compile(r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]')
        for dirpath, _dirnames, filenames in os.walk(os.path.join(self.workspace, "src")):
            for fn in filenames:
                if fn == "__init__.py":
                    init = os.path.join(dirpath, "__init__.py")
                    _logger.debug("🧞‍♀️ Found a potential module init in %s", init)
                    with open(init, "r") as inp:
                        for line in inp:
                            match = expr.match(line)
                            if match:
                                version = match.group(1)
                                _logger.debug("🔍 Using version «%s» from %s", version, init)
                                return version
        return None


class _SetupDetective(VersionDetective):
    """An abstract detective that refactors common behavior for detecting versions.

    Works for both ``setup.py`` and ``setup.cfg`` files.
    """

    def getfile(self):
        """Tell what file we're looking for."""
        raise NotImplementedError("Subclasses must implement ``getfile``")

    def getregexp(self):
        """Give us a good regexp to use in the file.

        The regexp must provide one capture group that contains the version string.
        """
        raise NotImplementedError("Subclasses must implement ``getregexp``")

    def detect(self):
        """Detect the version."""
        setupfile = self.findfile(self.getfile())
        if not setupfile:
            return None
        expr = self.getregexp()
        with open(setupfile, "r", encoding="utf-8") as inp:
            for line in inp:
                match = expr.search(line)
                if match:
                    return match.group(1).strip()
        return None


class SetupConfigDetective(_SetupDetective):
    """Detective that parses the ``seutp.cfg`` file for a declarative version."""

    def getfile(self):
        """Get the name of the file we're looking for."""
        return "setup.cfg"

    def getregexp(self):
        """Get regexp we're after inside of the file."""
        return re.compile(r"^version\s*=\s*([^#\s]+)")


class SetupModuleDetective(_SetupDetective):
    """Detective that parses the ``setup.py`` module for a programmatic version."""

    def getfile(self):
        """Get the name of the file we're looking for."""
        return "setup.py"

    def getregexp(self):
        """Get regexp we're after inside of the file."""
        return re.compile(r'version\s*=\s*[\'"]([^\'"]+)[\'"]')


# Functions
# ---------


def registerdetective(detective: type):
    """✍️ Register the given ``detective`` with the set of potential detetives."""
    if not issubclass(detective, VersionDetective):
        raise ValueError("Only register ``VersionDetective`` classes/subclasses with this function")
    _detectives.add(detective)


def getversion(workspace=None):
    """🕵️ Get a version.

    Get the version of a Python package in the given ``workspace``, or in the directory
    given by the ``GITHUB_WORKSPACE`` environment variable if it's set and non-empty,
    or the current working directory. Try several strategies to determine the version and
    use the one that makes the "most valid" version string, or raise a ``NoVersionDetectedError``
    if none of them look copacetic.
    """
    _logger.info("🤔 Python getversion called with workspace %s", workspace)

    # Figure out where to work
    gh = os.getenv("GITHUB_WORKSPACE")
    workspace = os.path.abspath(workspace if workspace else gh if gh else os.getcwd())
    _logger.debug("👣 The computed path is %s", workspace)

    # Try each detective
    versions = set()
    for detectiveclass in _detectives:
        detective = detectiveclass(workspace)
        version = detective.detect()
        _logger.debug("🔍 Detected version using %s is %r", detectiveclass.__name__, version)
        if version:
            # Validate it
            try:
                # In Python 3.13+, LegacyVersion is removed, so we just check if parsing succeeded
                # All valid versions are now Version objects, not LegacyVersion
                _ = packaging.version.parse(version)
                versions.add(version)
            except packaging.version.InvalidVersion:
                # Invalid, we won't add it
                pass

    # What we're left with are all valid so go with the shortest I guess; i.e., if one detective
    # said ``1.2.3`` but another said ``1.2.3.post4`` we prefer ``1.2.3``.
    if len(versions) == 0:
        raise NoVersionDetectedError()
    versions = list(versions)
    versions.sort(key=len)
    version = versions[0]
    _logger.debug("🏁 High confidence version is %s", version)
    return version


# Register the "built in" detectives:
for d in (
    VersioneerDetective,
    SetupConfigDetective,
    SetupModuleDetective,
    TextFileDetective,
    ModuleInitDetective,
):
    registerdetective(d)
