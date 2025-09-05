""" Functions for tergiversator """

import datetime
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile


def check_for(prog):
    """Make sure a program exists in our PATH"""

    if shutil.which(prog) is None:
        return False
    return True


def find_orphans(target, hostlist):
    """Display any directories not included in hostlists, and allow deletion"""

    folderlist = []
    for dirpath, dirnames, files in os.walk(target):  # pylint: disable=unused-variable
        for folder in dirnames:
            folderlist.append(os.path.join(dirpath, folder))

    configured = []
    for host_entry in hostlist:
        configured.append(target + "/" + host_entry)
        for path_entry in hostlist[host_entry]:
            if isinstance(path_entry, str):
                configured.append(target + "/" + host_entry + path_entry)

    spurious = []
    for path_entry in folderlist:
        found = 0
        for entry in configured:
            if re.match(entry, path_entry):
                found = 1
        if found == 0:
            spurious.append(path_entry)

    # sort results in descending length order
    spurious.sort(key=len)
    spurious.sort()
    spurious.reverse()

    return spurious


def create_index(hostlist, keystring, backup_path, my_env, _):
    """Take hostlist, keystring, backup path, and environment, and return file data"""

    datepattern = (
        r"([a-zA-Z]{3} [a-zA-Z]{3} [0-9 ]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4})"
    )
    filedata = []
    error_msg = ""
    for host in hostlist:
        for path in hostlist[host]:
            if not isinstance(path, str):
                continue
            try:
                for line in str(
                    subprocess.run(
                        (
                            f"duplicity{keystring}list-current-files"
                            + f" file://{backup_path}/{host}/{path}"
                        ).split(" "),
                        env=my_env,
                        capture_output=True,
                        check=True,
                    ).stdout
                ).split("\\n"):
                    split = re.match(datepattern, line)
                    if isinstance(split, re.Match):
                        datestring, filename = split.group(), line.replace(
                            f"{split.group()} ", ""
                        )
                        dateval = datetime.datetime.strptime(
                            datestring, "%a %b %d %H:%M:%S %Y"
                        ).isoformat()
                        filedata.append((f"{host}:{path}", dateval, filename))
            except subprocess.CalledProcessError as error:
                error_msg += _("Unable to index") + f" {host}:{path}:\n{error}\n"

    return filedata, error_msg


def write_index(file_data, backup_path):
    """Write file data to database"""

    error_msg = ""

    try:
        connection = sqlite3.connect(f"{backup_path}/index.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS files(host, datetime, path)")
        cursor.execute("DELETE FROM files;")
        cursor.executemany("INSERT INTO files VALUES(?, ?, ?)", file_data)
        connection.commit()
        return True, error_msg
    except sqlite3.Error as error:
        error_msg += f"{error}\n"
        return False, error_msg


def unmount_if_mounted(mount_path, my_env):
    """Unmount folder if it's a current mount point"""
    output = ""
    if os.path.ismount(mount_path):
        output = subprocess.run(
            ["umount", mount_path],
            env=my_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        ).stdout.decode()

    return output


def cleanup_mounts(mount_user, mount_host, mount_path, my_env):
    """Remove any stale filesystem mounts"""
    output = ""

    with open("/etc/mtab", "r", encoding="utf-8") as mtab:
        lines = [line.rstrip() for line in mtab]

    for line in lines:
        fields = line.split(" ")
        if fields[2] == "fuse.sshfs":
            if os.path.basename(fields[1]).startswith("tergiversator-"):
                if fields[0] == f"{mount_user}@{mount_host}:{mount_path}":
                    if os.path.ismount(fields[1]):
                        output += subprocess.run(
                            ["umount", fields[1]],
                            env=my_env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            check=True,
                        ).stdout.decode()
    return output


def mount_remote(
    mount_path, user, hostname, pathname, stricthostkey, port, unavailable
):
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    """Mount remote filesystem"""
    output = ""
    summary = ""
    brk = 0
    try:
        output += subprocess.run(
            [
                "sshfs",
                user + "@" + hostname + ":" + pathname,
                mount_path,
                "-o",
                f"StrictHostKeyChecking={stricthostkey}",
                "-p",
                f"{port}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        ).stdout.decode()
    except subprocess.CalledProcessError as error:
        output += f"{error}\n"
        summary += f"{hostname} - {unavailable}\n"
        brk = 1

    return output, summary, brk


def backup_host(hosts):
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    # pylint: disable=used-before-assignment
    """Backup all paths on a single host"""
    mountdir = tempfile.mkdtemp(prefix="tergiversator-")
    output = ""
    summary = ""
    host = hosts[0]
    for path in hosts[1]:
        if isinstance(path, dict):
            if "settings" in path:
                user = path.get("settings").get("user")
                port = path.get("settings").get("port")
                passphrase = path.get("settings").get("passphrase")
                backpath = path.get("settings").get("backpath")
                stricthostkey = path.get("settings").get("stricthostkey")
                keystring = path.get("settings").get("keystring")
                full_every = path.get("settings").get("full_every")
                retention = path.get("settings").get("retention")
                unable_to_process = path.get("settings").get("unable_to_process")
                error = path.get("settings").get("error")
                unavailable = path.get("settings").get("unavailable")

    my_env = os.environ.copy()
    my_env["PASSPHRASE"] = passphrase

    for path in hosts[1]:
        if not isinstance(path, str):
            continue

        output += f"--------------------\n{host}:{path}\n--------------------\n"

        # check if mounted
        output += unmount_if_mounted(mountdir, my_env)

        # clean up old mounts
        output += cleanup_mounts(user, host, path, my_env)

        # mount
        out, summ, brk = mount_remote(
            mountdir, user, host, path, stricthostkey, port, unavailable
        )
        if brk == 1:
            output += out
            summary += summ
            break

        # backup
        cleanup = (
            f"duplicity{keystring}--allow-source-mismatch -v0 cleanup --force file://"
            + backpath
            + "/"
            + host
            + path
        )
        backup = (
            f"duplicity{keystring}--allow-source-mismatch incremental "
            + "--full-if-older-than "
            + full_every
            + " "
            + mountdir
            + " file://"
            + backpath
            + "/"
            + host
            + path
        )
        prune = (
            f"duplicity{keystring}--allow-source-mismatch -v0 remove-older-than "
            + retention
            + " file://"
            + backpath
            + "/"
            + host
            + path
            + " --force"
        )

        erred = 0

        for command in [cleanup, backup, prune]:
            try:
                cmdout = subprocess.run(
                    command.split(" "),
                    env=my_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=True,
                )
                output += cmdout.stdout.decode()
            except subprocess.CalledProcessError as local_error:
                output += f"{unable_to_process}: {command}\n{error}\n"
                output += f"{command}\n{cmdout.stdout.decode()}\n"
                output += f"{local_error}\n"
                erred = 1

        if erred == 1:
            summary += f"{host}:{path} - Duplicity {error}\n"
        else:
            summary += f"{host}:{path} - OK\n"
        # unmount
        os.sync()

        umount_out = subprocess.run(
            ["umount", mountdir],
            env=my_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
        while umount_out.returncode != 0:
            umount_out = subprocess.run(
                ["umount", mountdir],
                env=my_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
            )

    # Cleanup
    os.rmdir(mountdir)

    return summary, output
