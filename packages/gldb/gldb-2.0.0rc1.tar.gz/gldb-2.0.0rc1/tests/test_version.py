import json
import pathlib
import unittest
from datetime import datetime

from gldb import __version__


def get_package_meta():
    """Reads codemeta.json and returns it as dict"""
    with open(__this_dir__ / '../codemeta.json', 'r') as f:
        codemeta = json.loads(f.read())
    return codemeta


__this_dir__ = pathlib.Path(__file__).parent


class TestVersion(unittest.TestCase):

    def test_version(self):
        this_version = 'x.x.x'
        setupcfg_filename = __this_dir__ / '../setup.cfg'
        with open(setupcfg_filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'version' in line:
                    this_version = line.split(' = ')[-1].strip()
        self.assertEqual(__version__, this_version)

    def test_codemeta(self):
        """checking if the version in codemeta.json is the same as the one of the toolbox"""

        codemeta = get_package_meta()
        codemeta_version = codemeta["version"]
        if "-rc." in codemeta_version:
            codemeta_version = codemeta_version.replace("-rc.", "rc")
        self.assertEqual(__version__, codemeta_version)


    def test_citation_cff(self):
        """checking if the version in CITATION.cff is the same as the one of the ssnolib"""
        this_version = 'x.x.x'
        dt = None
        setupcfg_filename = __this_dir__ / '../CITATION.cff'
        with open(setupcfg_filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'version:' in line:
                    this_version = line.split(':')[-1].strip()
                elif 'date-released:' in line:
                    # check if the date is the same as the one in codemeta.json
                    date_str = line.split(':')[-1].strip()
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
        if "-rc." in this_version:
            this_version = this_version.replace("-rc.", "rc")
        self.assertEqual(__version__, this_version)
        self.assertEqual(dt.strftime('%Y-%m-%d'), datetime.now().date().strftime('%Y-%m-%d'))