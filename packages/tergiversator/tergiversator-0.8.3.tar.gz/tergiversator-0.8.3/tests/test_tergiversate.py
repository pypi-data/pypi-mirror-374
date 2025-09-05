""" Unit tests for tergiversate """

# Copyright (C) 2024 Gwyn Ciesla

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gettext
import os

import tergiversate

HOST_LIST = {"hostname": ["/etc", "/root", 42, "/home"]}
PASSPHRASE = "testphrase"
MY_ENV = os.environ.copy()
BACKUP_PATH = "tests/sample/backups/"
BACKUP_PATH_BAD = "tests/sample/bogus/"
INDEX = [
    ("hostname:/etc", "2024-08-21T08:54:41", "."),
    ("hostname:/etc", "2024-08-21T08:54:41", "resolv.conf"),
    ("hostname:/root", "2024-08-21T08:52:38", "."),
    ("hostname:/home", "2024-08-21T08:54:02", "."),
    ("hostname:/home", "2024-08-21T08:54:02", "hi.txt"),
]
LOCALEDIR = os.path.dirname(tergiversate.__file__) + "/locales"
LANGUAGE = os.environ["LANG"]
if not os.path.isdir(LOCALEDIR + "/" + LANGUAGE):
    LANGUAGE = "en"
TRANS = gettext.translation("tergiversate", localedir=LOCALEDIR, languages=[LANGUAGE])
TRANS.install()
_ = TRANS.gettext


def test_check_for():
    """Test that this function can locate /bin/sh"""
    assert tergiversate.check_for("sh")
    assert not tergiversate.check_for("thisshouldalwaysfail")


def test_find_orphans():
    """Test that find_orphans can locate an unconfigured folder"""
    targ = os.path.dirname(BACKUP_PATH)
    succeed = False
    for result in tergiversate.find_orphans(targ, HOST_LIST):
        print(result)
        if "red" in result:
            succeed = True
    assert succeed


def test_create_index():
    """Test indexing of backups"""
    MY_ENV["PASSPHRASE"] = PASSPHRASE
    # Set timezone to match where the data data was created.
    MY_ENV["TZ"] = "America/Chicago"
    fdata, errors = tergiversate.create_index(HOST_LIST, " ", BACKUP_PATH, MY_ENV, _)
    assert (fdata == INDEX) and (len(errors) == 0)


def test_write_index():
    """Test writing index to database file"""
    result, errors = tergiversate.write_index(INDEX, BACKUP_PATH)
    if result:
        os.remove(f"{BACKUP_PATH}/index.db")
    assert (result) and (len(errors) == 0)

    result, errors = tergiversate.write_index(INDEX, BACKUP_PATH_BAD)
    if result:
        os.remove(f"{BACKUP_PATH_BAD}/index.db")
    assert not (result) and (len(errors) > 0)
