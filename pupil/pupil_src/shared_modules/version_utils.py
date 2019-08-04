# -*- coding: utf-8 -*-
# Author: Douglas Creager <dcreager@dcreager.net>
# Changes, Additions: Moritz Kassner <moritz@pupil-labs.com>, Will Patera <will@pupil-labs.com>
# This file is placed into the public domain.

from subprocess import check_output, CalledProcessError, STDOUT
import os, sys
from distutils.version import LooseVersion as VersionFormat


import logging

logger = logging.getLogger(__name__)


def get_tag_commit():
    """
    returns string: 'tag'-'commits since tag'-'7 digit commit id'
    """
    try:
        desc_tag = check_output(
            ["git", "describe", "--tags", "--long"],
            stderr=STDOUT,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        desc_tag = desc_tag.decode("utf-8")
        desc_tag = desc_tag.replace("\n", "")  # strip newlines
        return desc_tag
    except CalledProcessError as e:
        logger.error('Error calling git: "{}" \n output: "{}"'.format(e, e.output))
        return None
    except OSError as e:
        logger.error('Could not call git, is it installed? error msg: "{}"'.format(e))
        return None


def pupil_version():
    """
    [major].[minor].[trailing-untagged-commits]
    """
    version = get_tag_commit()
    if version is None:
        raise ValueError("Version Error")

    version = version.replace("v", "")  # strip version 'v'
    # print(version)
    if "-" in version:
        parts = version.split("-")
        version = ".".join(parts[:-1])
    return version


def get_version(version_file=None):
    # get the current software version
    if getattr(sys, "frozen", False):
        with open(version_file, "r") as f:
            version = f.read()
    else:
        version = pupil_version()
    version = VersionFormat(version)
    logger.debug("Running version: {}".format(version))
    return version


def read_rec_version(meta_info):
    version = meta_info.get(
        "Data Format Version", meta_info["Capture Software Version"]
    )
    version = "".join(
        [c for c in version if c in "1234567890.-"]
    )  # strip letters in case of legacy version format
    version = VersionFormat(version)
    logger.debug("Recording version: {}".format(version))
    return version


def write_version_file(target_dir):
    version = pupil_version()
    print("Current version of Pupil: ", version)

    with open(os.path.join(target_dir, "_version_string_"), "w") as f:
        f.write(version)
    print("Wrote version into: {}".format(os.path.join(target_dir, "_version_string_")))


if __name__ == "__main__":
    print(get_tag_commit())
    print(pupil_version())
