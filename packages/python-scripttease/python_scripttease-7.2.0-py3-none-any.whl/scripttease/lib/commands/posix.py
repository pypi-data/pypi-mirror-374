import os
from .base import Command, MultipleCommands, Prompt


def append(path, content=None, **kwargs):
    """Append content to a file.

    :param path: The path to the file.
    :type path: str

    :param content: The content to be appended.
    :type content: str

    """
    kwargs.setdefault("comment", "append to %s" % path)

    statement = 'echo "%s" >> %s' % (content or "", path)

    return Command(statement, **kwargs)


def archive(from_path, absolute=False, exclude=None, file_name="archive.tgz", strip=None, to_path=".", view=False,
            **kwargs):
    """Create a file archive.

    :param from_path: The path that should be archived.
    :type from_path: str

    :param absolute: Set to ``True`` to preserve the leading slash.
    :type absolute: bool

    :param exclude: A pattern to be excluded from the archive.
    :type exclude: str

    :param file_name: The name of the archive file.
    :type file_name: str

    :param strip: Remove the specified number of leading elements from the path.
    :type strip: int

    :param to_path: Where the archive should be created. This should *not* include the file name.
    :type to_path: str

    :param view: View the output of the command as it happens.
    :type view: bool

    """
    tokens = ["tar"]
    switches = ["-cz"]

    if absolute:
        switches.append("P")

    if view:
        switches.append("v")

    tokens.append("".join(switches))

    if exclude:
        tokens.append("--exclude %s" % exclude)

    if strip:
        tokens.append("--strip-components %s" % strip)

    to_path = "%s/%s" % (to_path, file_name)
    tokens.append('-f %s %s' % (to_path, from_path))

    name = " ".join(tokens)

    return Command(name, **kwargs)


def certbot(domain_name, email=None, webroot=None, **kwargs):
    """Get new SSL certificate from Let's Encrypt.

    :param domain_name: The domain name for which the SSL certificate is requested.
    :type domain_name: str

    :param email: The email address of the requester sent to the certificate authority. Required.
    :type email: str

    :param webroot: The directory where the challenge file will be created.
    :type webroot: str

    """
    _email = email or os.environ.get("SCRIPTTEASE_CERTBOT_EMAIL", None)
    _webroot = webroot or os.path.join("/var", "www", "domains", domain_name.replace(".", "_"), "www")

    if not _email:
        raise ValueError("Email is required for certbot command.")

    template = "certbot certonly --agree-tos --email %(email)s -n --webroot -w %(webroot)s -d %(domain_name)s"
    statement = template % {
        'domain_name': domain_name,
        'email': _email,
        'webroot': _webroot,
    }

    return Command(statement, **kwargs)


def copy(from_path, to_path, overwrite=False, recursive=False, **kwargs):
    """Copy a file or directory.

    :param from_path: The file or directory to be copied.
    :type from_path: str

    :param to_path: The location to which the file or directory should be copied.
    :type to_path: str

    :param overwrite: Indicates files and directories should be overwritten if they exist.
    :type overwrite: bool

    :param recursive: Copy sub-directories.
    :type recursive: bool

    """
    kwargs.setdefault("comment", "copy %s to %s" % (from_path, to_path))

    a = list()
    a.append("cp")

    if not overwrite:
        a.append("-n")

    if recursive:
        a.append("-R")

    a.append(from_path)
    a.append(to_path)

    return Command(" ".join(a), **kwargs)


def directory(path, group=None, mode=None, owner=None, recursive=False, **kwargs):
    """Create a directory.

    :param path: The path to be created.
    :type path: str

    :param mode: The access permissions of the new directory.
    :type mode: int | str

    :param recursive: Create all directories along the path.
    :type recursive: bool

    """
    comment = kwargs.pop("comment", "create directory %s" % path)

    statement = ["mkdir"]
    if mode is not None:
        statement.append("-m %s" % mode)

    if recursive:
        statement.append("-p")

    statement.append(path)

    mkdir = Command(" ".join(statement), comment=comment, **kwargs)

    chgrp = None
    if group:
        if recursive:
            chgrp = Command("chgrp -R %s %s" % (group, path), comment="set %s group on %s" % (group, path), **kwargs)
        else:
            chgrp = Command("chgrp %s %s" % (group, path), comment="set %s group on %s" % (group, path), **kwargs)

    chown = None
    if owner:
        if recursive:
            chown = Command("chown -R %s %s" % (owner, path), comment="set %s owner on %s" % (owner, path), **kwargs)
        else:
            chown = Command("chown %s %s" % (owner, path), comment="set %s owner on %s" % (owner, path), **kwargs)

    commands = list()
    commands.append(mkdir)
    if chgrp is not None:
        commands.append(chgrp)

    if chown is not None:
        commands.append(chown)

    if len(commands) == 1:
        return commands[0]

    return MultipleCommands(commands, comment=comment)


def extract(from_path, absolute=False, exclude=None, strip=None, to_path=None, view=False, **kwargs):
    """Extract a file archive.

    :param from_path: The path to be extracted.
    :type from_path: str

    :param absolute: Set to ``True`` to preserve the leading slash.
    :type absolute: bool

    :param exclude: A pattern to be excluded from the extraction.
    :type exclude: str

    :param strip: Remove the specified number of leading elements from the path.
    :type strip: int

    :param to_path: Where the extraction should occur.
    :type to_path: str

    :param view: View the output of the command as it happens.
    :type view: bool

    """
    _to_path = to_path or "./"

    tokens = ["tar"]
    switches = ["-xz"]

    if absolute:
        switches.append("P")

    if view:
        switches.append("v")

    tokens.append("".join(switches))

    if exclude:
        tokens.append("--exclude %s" % exclude)

    if strip:
        tokens.append("--strip-components %s" % strip)

    tokens.append('-f %s %s' % (from_path, _to_path))

    statement = " ".join(tokens)

    return Command(statement, **kwargs)


def link(source, force=False, target=None, **kwargs):
    """Create a symlink.

    :param source: The source of the link.
    :type source: str

    :param force: Force the creation of the link.
    :type force: bool

    :param target: The name or path of the target. Defaults to the base name of the source path.
    :type target: str

    """
    _target = target or os.path.basename(source)

    kwargs.setdefault("comment", "link to %s" % source)

    statement = ["ln -s"]

    if force:
        statement.append("-f")

    statement.append(source)
    statement.append(_target)

    return Command(" ".join(statement), **kwargs)


def move(from_path, to_path, **kwargs):
    """Move a file or directory.

    :param from_path: The current path.
    :type from_path: str

    :param to_path: The new path.
    :type to_path: str

    """
    kwargs.setdefault("comment", "move %s to %s" % (from_path, to_path))
    statement = "mv %s %s" % (from_path, to_path)

    return Command(statement, **kwargs)


def perms(path, group=None, mode=None, owner=None, recursive=False, **kwargs):
    """Set permissions on a file or directory.

    :param path: The path to be changed.
    :type path: str

    :param group: The name of the group to be applied.
    :type group: str

    :param mode: The access permissions of the file or directory.
    :type mode: int | str

    :param owner: The name of the user to be applied.
    :type owner: str

    :param recursive: Update all files and directories along the path.
    :type recursive: bool

    """
    comment = kwargs.pop("comment", "set permissions on %s" % path)

    chgrp = None
    if group is not None:
        a = ["chgrp"]

        if recursive:
            a.append("-R")

        a.append(group)
        a.append(path)

        chgrp = Command(" ".join(a), comment="set %s group on %s" % (group, path), **kwargs)

    chmod = None
    if mode is not None:
        a = ["chmod"]

        if recursive:
            a.append("-R")

        a.append(str(mode))
        a.append(path)

        chmod = Command(" ".join(a), comment="set %s mode on %s" % (mode, path), **kwargs)

    chown = None
    if owner is not None:
        a = ["chown"]

        if recursive:
            a.append("-R")

        a.append(owner)
        a.append(path)

        chown = Command(" ".join(a), comment="set %s owner on %s" % (owner, path), **kwargs)

    commands = list()
    if chgrp is not None:
        commands.append(chgrp)

    if chmod is not None:
        commands.append(chmod)

    if chown is not None:
        commands.append(chown)

    if len(commands) == 1:
        return commands[0]

    return MultipleCommands(commands, comment=comment, **kwargs)


def prompt(name, back_title="Input", choices=None, default=None, dialog=False, help_text=None, label=None, **kwargs):
    """Prompt the user for input.

    :param name: The programmatic name of the input.
    :type name: str

    :param back_title: The back title used with the dialog command.
    :type back_title: str

    :param choices: A list of valid choices.
    :type choices: list | str

    :param default: The default value.
    :type default: str

    :param dialog: Use a dialog command for the prompt.
    :type dialog: bool

    :param help_text: The text to display with the dialog command.
    :type help_text: str

    :param label: The label for the input.
    :type label: str

    """
    return Prompt(
        name,
        back_title=back_title,
        choices=choices,
        default=default,
        dialog=dialog,
        help_text=help_text,
        label=label,
        **kwargs
    )


def remove(path, force=False, recursive=False, **kwargs):
    """Remove a file or directory.

    :param path: The path to be removed.
    :type path: str

    :param force: Force the removal.
    :type force: bool

    :param recursive: Remove all directories along the path.
    :type recursive: bool

    """
    kwargs.setdefault("comment", "remove %s" % path)

    statement = ["rm"]

    if force:
        statement.append("-f")

    if recursive:
        statement.append("-r")

    statement.append(path)

    return Command(" ".join(statement), **kwargs)


def replace(path, backup=".b", delimiter="/", find=None, sub=None, **kwargs):
    """Find and replace text in a file.

    :param path: The path to the file to be edited.
    :type path: str

    :param backup: The backup file extension to use.
    :type backup: str

    :param delimiter: The pattern delimiter.
    :type delimiter: str

    :param find: The old text. Required.
    :param find: str

    :param sub: The new text. Required.
    :type sub: str

    """

    kwargs.setdefault("comment", "find and replace in %s" % path)

    context = {
        'backup': backup,
        'delimiter': delimiter,
        'path': path,
        'pattern': find,
        'replace': sub,
    }

    template = "sed -i %(backup)s 's%(delimiter)s%(pattern)s%(delimiter)s%(replace)s%(delimiter)sg' %(path)s"

    statement = template % context

    return Command(statement, **kwargs)


def run(statement, **kwargs):
    """Run any command.

    :param statement: The statement to be executed.
    :type statement: str

    """
    kwargs.setdefault("comment", "run statement")

    return Command(statement, **kwargs)


def rsync(source, target, delete=False, exclude=None, host=None, key_file=None, links=True, port=22,
          recursive=True, user=None, **kwargs):
    """Synchronize a directory structure.

    :param source: The source directory.
    :type source: str

    :param target: The target directory.
    :type target: str

    :param delete: Indicates target files that exist in source but not in target should be removed.
    :type delete: bool

    :param exclude: The path to an exclude file.
    :type exclude: str

    :param host: The host name or IP address.
    :type host: str

    :param key_file: The privacy SSH key (path) for remote connections. User expansion is automatically applied.
    :type key_file: str

    :param links: Include symlinks in the sync.
    :type links: bool

    :param port: The SSH port to use for remote connections.
    :type port: int

    :param recursive: Indicates source contents should be recursively synchronized.
    :type recursive: bool

    :param user: The username to use for remote connections.
    :type user: str

    """
    # - guess: When ``True``, the ``host``, ``key_file``, and ``user`` will be guessed based on the base name of
    #               the source path.
    # :type guess: bool
    # if guess:
    #     host = host or os.path.basename(source).replace("_", ".")
    #     key_file = key_file or os.path.expanduser(os.path.join("~/.ssh", os.path.basename(source)))
    #     user = user or os.path.basename(source)
    # else:
    #     host = host
    #     key_file = key_file
    #     user = user

    kwargs.setdefault("comment", "sync %s with %s" % (source, target))

    # rsync -e "ssh -i $(SSH_KEY) -p $(SSH_PORT)" -P -rvzc --delete
    # $(OUTPUTH_PATH) $(SSH_USER)@$(SSH_HOST):$(UPLOAD_PATH) --cvs-exclude;

    # ansible:
    # /usr/bin/rsync --delay-updates -F --compress --delete-after --copy-links --archive --rsh='/usr/bin/ssh -S none -
    # i /home/shawn/.ssh/sharedservices_group -o Port=4894 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
    # --rsync-path='sudo -u root rsync'
    # --exclude-from=/home/shawn/Work/app_sharedservices_group/deploy/roles/project/rsync.txt
    # --out-format='<<CHANGED>>%i %n%L'

    tokens = list()
    tokens.append("rsync")
    # BUG: Providing rsync --cvs-exclude was causing directories named "tags" to be omitted.
    # tokens.append("--cvs-exclude")
    tokens.append("--exclude=.git")
    tokens.append("--checksum")
    tokens.append("--compress")

    if links:
        tokens.append("--copy-links")

    if delete:
        tokens.append("--delete")

    if exclude is not None:
        # tokens.append("--exclude-from={'%s'}" % exclude)
        tokens.append("--exclude-from=%s" % exclude)

    # --partial and --progress
    tokens.append("-P")

    if recursive:
        tokens.append("--recursive")

    tokens.append(source)

    conditions = [
        host is not None,
        key_file is not None,
        user is not None,
    ]
    if all(conditions):
        tokens.append('-e "ssh -i %s -p %s"' % (key_file, port))
        tokens.append("%s@%s:%s" % (user, host, target))
    else:
        tokens.append(target)

    statement = " ".join(tokens)

    return Command(statement, **kwargs)


def scopy(from_path, to_path, host=None, key_file=None, port=22, user=None, **kwargs):
    """Copy a file or directory to a remote server.

    :param from_path: The source of the copy.
    :type from_path: str

    :param to_path: The remote target of the copy.
    :type to_path: str

    :param host: The host name or IP address. Required.
    :type host: str

    :param key_file: The privacy SSH key (path) for remote connections. User expansion is automatically applied.
    :type key_file: str

    :param port: The SSH port to use for remote connections.
    :type port: int

    :param user: The username to use for remote connections.
    :type user: str

    """
    kwargs.setdefault("comment", "copy %s to remote %s" % (from_path, to_path))

    # TODO: What to do to force local versus remote commands?
    # kwargs['local'] = True

    kwargs['sudo'] = False

    statement = ["scp"]

    if key_file is not None:
        statement.append("-i %s" % key_file)

    statement.append("-P %s" % port)
    statement.append(from_path)

    if host is not None and user is not None:
        statement.append("%s@%s:%s" % (user, host, to_path))
    elif host is not None:
        statement.append("%s:%s" % (host, to_path))
    else:
        raise ValueError("Host is a required keyword argument.")

    return Command(" ".join(statement), **kwargs)


def sync(source, target, delete=False, exclude=None, links=True, recursive=True, **kwargs):
    """Synchronize a local directory structure.

    :param source: The source directory.
    :type source: str

    :param target: The target directory.
    :type target: str

    :param delete: Indicates target files that exist in source but not in target should be removed.
    :type delete: bool

    :param exclude: The path to an exclude file.
    :type exclude: str

    :param links: Include symlinks in the sync.
    :type links: bool

    :param recursive: Indicates source contents should be recursively synchronized.
    :type recursive: bool

    """
    # - guess: When ``True``, the ``host``, ``key_file``, and ``user`` will be guessed based on the base name of
    #               the source path.
    # :type guess: bool
    # if guess:
    #     host = host or os.path.basename(source).replace("_", ".")
    #     key_file = key_file or os.path.expanduser(os.path.join("~/.ssh", os.path.basename(source)))
    #     user = user or os.path.basename(source)
    # else:
    #     host = host
    #     key_file = key_file
    #     user = user

    kwargs.setdefault("comment", "sync %s with %s" % (source, target))

    # rsync -e "ssh -i $(SSH_KEY) -p $(SSH_PORT)" -P -rvzc --delete
    # $(OUTPUTH_PATH) $(SSH_USER)@$(SSH_HOST):$(UPLOAD_PATH) --cvs-exclude;

    tokens = list()
    tokens.append("rsync")
    # tokens.append("--cvs-exclude")
    tokens.append("--exclude=.git")
    tokens.append("--checksum")
    tokens.append("--compress")

    if links:
        tokens.append("--copy-links")

    if delete:
        tokens.append("--delete")

    if exclude is not None:
        # tokens.append("--exclude-from={'%s'}" % exclude)
        tokens.append("--exclude-from=%s" % exclude)

    # --partial and --progress
    tokens.append("-P")

    if recursive:
        tokens.append("--recursive")

    tokens.append(source)
    tokens.append(target)

    statement = " ".join(tokens)

    return Command(statement, **kwargs)


def touch(path, **kwargs):
    """Touch a file or directory.

    :param path: The file or directory to touch.
    :type path: str

    """
    kwargs.setdefault("comment", "touch %s" % path)

    return Command("touch %s" % path, **kwargs)


def wait(seconds, **kwargs):
    """Pause execution for a number of seconds.

    :param seconds: The number of seconds to wait.
    :type seconds: int

    """
    kwargs.setdefault("comment", "pause for %s seconds" % seconds)

    return Command("sleep %s" % seconds, **kwargs)


def write(path, content=None, **kwargs):
    """Write to a file.

    :param path: The file to be written.
    :type path: str

    :param content: The content to be written. Note: If omitted, this command is equivalent to ``touch``.
    :type content: str

    """
    _content = content or ""

    kwargs.setdefault("comment", "write to %s" % path)

    # We need the normalized sudo below.
    command = Command("", **kwargs)

    a = list()

    if len(_content.split("\n")) > 1:
        cat = "cat > %s << EOF" % path
        if command.sudo:
            cat = "cat << 'EOF' | %s tee > %s" % (command.sudo, path)

        a.append(cat)
        a.append(_content)
        a.append("EOF")
    else:
        echo = 'echo "%s" > %s' % (_content, path)
        if command.sudo:
            echo = 'echo "%s" | %s tee > %s' % (_content, command.sudo, path)

        a.append(echo)

    command.statement = " ".join(a)

    return command


POSIX_MAPPINGS = {
    'append': append,
    'archive': archive,
    'certbot': certbot,
    'copy': copy,
    'dir': directory,
    'extract': extract,
    'link': link,
    'move': move,
    'perms': perms,
    'prompt': prompt,
    'push': rsync,
    'remove': remove,
    'replace': replace,
    'run': run,
    'rsync': rsync,
    'scopy': scopy,
    'ssl': certbot,
    'sync': sync,
    'touch': touch,
    'wait': wait,
    'write': write,
}
