# Tergiversator

##### Run multiple duplicity backups from a central host

### Installation

`pip3 install -r requirements.txt`

You'll also need `duplicity` and `sshfs` (from fuse-sshfs) in your PATH.

### Setup

Copy `config.yml.example` to one of:

1. `config.yml`
2. `~/.tergiversator/config.yml`
3. `/etc/tergiversator/config.yml`.

Tergiversator will use the first file found in that sequence unless one 
is specified at runtime.

Example:

```
---
config:
  retention: "2M"
  full_every: "1M"
  user: "root"
  path: "backups"
  passphrase: "chooseyourown"
  keyid: "" #typically 40 characters, see gpg -K
  hostlist: "hostlist.yml"
  strict_hostkey_checking: "no"
  autoindex: "no"
  ssh_port: "22"
  processes: "0" # Number of hosts to backup in parallel. 
                 # 0 will result in one parallel task per logical CPU.
```

Note: specify a user that the running user can access via ssh on the remote hosts.
If you intend to automate/schedule backups, a passwordless ssh key is recommended.
Ideally, the private key will only be present in the running user's `~/.ssh/`,
the public key only in the remote users' `~/.ssh/authorized_hosts` files.

SSH and GPG key distribution should be done as securely as possible.

Copy `hostlist.yml.example` to `hostlist.yml`, located somewhere the user
running Tergiversator can read. Specify the path in your `config.yaml`.
Edit this file to include hosts and the paths on those hosts you want to back up.

Example:

```
---
samplehost:
  - /etc
  - /home
anotherhost.domain:
  - /root
  - /opt/something/else
  - settings: {user: anotheruser, port: 8022} #optional settings for this host

```
### Usage

`./tergiversator [-h] [-c CONFIG] [COMMAND]`

positional arguments:
  COMMAND               prune | index | search | restore

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to configuration file



Running without a command will back up all configured hosts/paths.
If only a passphrase is provided, backups will use symmetric encryption.
If a keyid is provided, asymmetric encryption will be used,
using the passphrase provided to unlock the key. Make sure the trust level
on the key you're using is set to `ultimate`.

### Commands:

`prune`

This will locate any host/path combinations that exist in the
backup path that aren't in the hostlist.yml, and offer to let you delete them.
Good for saving space iif needs change.

`index`

Generates a sqlite3 database in the backup path folder with the
contents of all backups. If one exists, it will be replaced with an updated
version.

`search`

Will ask for a search string, and then return a list of all file paths
containing that string. Requires an `index` run first.

`restore`

Will ask you for:

- host and path choices
- whether you want to restore locally or to your remote user's homedir

and then restore to a unique folder in the chosen destination.

*You'll see errors for symlinks, since the paths won't be valid. This is normal.*

You can then place the desired files in their final destinations.

---

Copyright (C) 2025 Gwyn Ciesla
