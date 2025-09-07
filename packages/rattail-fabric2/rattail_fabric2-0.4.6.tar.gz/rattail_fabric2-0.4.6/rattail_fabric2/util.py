# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Misc. Utilities
"""

import hashlib


def exists(c, path, use_sudo=False):
    """
    Return True if given path exists on the current remote host.

    If ``use_sudo`` is True, will use `sudo` instead of `run`.

    .. note::

       This function is derived from one copied from fabric v1.
    """
    func = c.sudo if use_sudo else c.run
    cmd = 'stat %s' % _expand_path(c, path)
    return not func(cmd, warn=True).failed


def contains(c, filename, text, exact=False, use_sudo=False, escape=True,
             shell=False, case_sensitive=True):
    """
    NOTE: This was copied from the upstream ``fabric.contrib.files`` (v1) module.

    Return True if ``filename`` contains ``text`` (which may be a regex.)

    By default, this function will consider a partial line match (i.e. where
    ``text`` only makes up part of the line it's on). Specify ``exact=True`` to
    change this behavior so that only a line containing exactly ``text``
    results in a True return value.

    This function leverages ``egrep`` on the remote end (so it may not follow
    Python regular expression syntax perfectly), and skips ``env.shell``
    wrapper by default.

    If ``use_sudo`` is True, will use `sudo` instead of `run`.

    If ``escape`` is False, no extra regular expression related escaping is
    performed (this includes overriding ``exact`` so that no ``^``/``$`` is
    added.)

    The ``shell`` argument will be eventually passed to ``run/sudo``. See
    description of the same argument in ``~fabric.contrib.sed`` for details.

    If ``case_sensitive`` is False, the `-i` flag will be passed to ``egrep``.
    """
    func = use_sudo and c.sudo or c.run
    if escape:
        text = _escape_for_regex(text)
        if exact:
            text = "^%s$" % text
    # TODO: do we need to bother hiding things here?
    # with settings(hide('everything'), warn_only=True):
    egrep_cmd = 'egrep "%s" %s' % (text, _expand_path(c, filename))
    if not case_sensitive:
        egrep_cmd = egrep_cmd.replace('egrep', 'egrep -i', 1)
    return not func(egrep_cmd, shell=shell, warn=True).failed


def append(c, filename, text, use_sudo=False, partial=False, escape=True,
           shell=False):
    """
    NOTE: This was copied from the upstream ``fabric.contrib.files`` (v1) module.

    Append string (or list of strings) ``text`` to ``filename``.

    When a list is given, each string inside is handled independently (but in
    the order given.)

    If ``text`` is already found in ``filename``, the append is not run, and
    None is returned immediately. Otherwise, the given text is appended to the
    end of the given ``filename`` via e.g. ``echo '$text' >> $filename``.

    The test for whether ``text`` already exists defaults to a full line match,
    e.g. ``^<text>$``, as this seems to be the most sensible approach for the
    "append lines to a file" use case. You may override this and force partial
    searching (e.g. ``^<text>``) by specifying ``partial=True``.

    Because ``text`` is single-quoted, single quotes will be transparently
    backslash-escaped. This can be disabled with ``escape=False``.

    If ``use_sudo`` is True, will use `sudo` instead of `run`.

    The ``shell`` argument will be eventually passed to ``run/sudo``. See
    description of the same argumnet in ``~fabric.contrib.sed`` for details.
    """
    func = use_sudo and c.sudo or c.run
    # Normalize non-list input to be a list
    if isinstance(text, str):
        text = [text]
    for line in text:
        regex = '^' + _escape_for_regex(line)  + ('' if partial else '$')
        if (exists(c, filename, use_sudo=use_sudo) and line
            and contains(c, filename, regex, use_sudo=use_sudo, escape=False,
                         shell=shell)):
            continue
        if escape:
            line = line.replace("'", r"'\\''") # TODO: does this one even work?
            line = line.replace('"', r'\"')
            line = line.replace('$', r'\$')
        func("""bash -c "echo '%s' >> %s" """ % (line, _expand_path(c, filename)))


def _escape_for_regex(text):
    """
    NOTE: This was copied from the upstream ``fabric.contrib.files`` (v1) module.

    Escape ``text`` to allow literal matching using egrep
    """
    re_specials = '\\^$|(){}[]*+?.'
    sh_specials = '\\$`"'
    re_chars = []
    sh_chars = []

    for c in text:
        if c in re_specials:
            re_chars.append('\\')
        re_chars.append(c)

    for c in re_chars:
        if c in sh_specials:
            sh_chars.append('\\')
        sh_chars.append(c)

    return ''.join(sh_chars)


def is_win(c):
    """
    Return True if remote SSH server is running Windows, False otherwise.

    The idea is based on echoing quoted text: \*NIX systems will echo quoted
    text only, while Windows echoes quotation marks as well.

    .. note::

       This function is derived from one copied from fabric v1.
    """
    result = c.run('echo "Will you echo quotation marks"', warn=True)
    return '"' in result.stdout


def _expand_path(c, path):
    """
    Return a path expansion

    E.g.    ~/some/path     ->  /home/myuser/some/path
            /user/\*/share   ->  /user/local/share
    More examples can be found here: http://linuxcommand.org/lc3_lts0080.php

    .. versionchanged:: 1.0
        Avoid breaking remote Windows commands which does not support expansion.

    .. note::

       This function is derived from one copied from fabric v1.
    """
    return path if is_win(c) else '"$(echo %s)"' % path


def get_home_path(c, user=None):
    """
    Retrieve the path to the home folder for the given user, or else the
    "connection" user.
    """
    user = user or c.user
    home = c.run('getent passwd {} | cut -d: -f6'.format(user)).stdout.strip()
    home = home.rstrip('/')
    return home


def sed(c, filename, before, after, limit='', use_sudo=False, backup='.bak',
        flags='',
        # shell=False,
):
    """
    NOTE: This was copied from the upstream ``fabric.contrib.files`` (v1) module.

    Run a search-and-replace on ``filename`` with given regex patterns.

    Equivalent to ``sed -i<backup> -r -e "/<limit>/ s/<before>/<after>/<flags>g"
    <filename>``. Setting ``backup`` to an empty string will, disable backup
    file creation.

    For convenience, ``before`` and ``after`` will automatically escape forward
    slashes, single quotes and parentheses for you, so you don't need to
    specify e.g.  ``http:\/\/foo\.com``, instead just using ``http://foo\.com``
    is fine.

    If ``use_sudo`` is True, will use `sudo` instead of `run`.

    ..
       The ``shell`` argument will be eventually passed to `run`/`sudo`. It
       defaults to False in order to avoid problems with many nested levels of
       quotes and backslashes. However, setting it to True may help when using
       ``~fabric.operations.cd`` to wrap explicit or implicit ``sudo`` calls.
       (``cd`` by it's nature is a shell built-in, not a standalone command, so it
       should be called within a shell.)

    Other options may be specified with sed-compatible regex flags -- for
    example, to make the search and replace case insensitive, specify
    ``flags="i"``. The ``g`` flag is always specified regardless, so you do not
    need to remember to include it when overriding this parameter.
    """
    func = use_sudo and c.sudo or c.run
    # Characters to be escaped in both
    for char in "/'":
        before = before.replace(char, r'\%s' % char)
        after = after.replace(char, r'\%s' % char)
    # Characters to be escaped in replacement only (they're useful in regexen
    # in the 'before' part)
    for char in "()":
        after = after.replace(char, r'\%s' % char)
    if limit:
        limit = r'/%s/ ' % limit

    # if replacement text contains single quote chars, must escape them
    after = after.replace("'", "'\"'\"'")

    context = {
        'script': r"'%ss/%s/%s/%sg'" % (limit, before, after, flags),
        'filename': _expand_path(c, filename),
        'backup': backup
    }
    # Test the OS because of differences between sed versions

    # with hide('running', 'stdout'):
    #     platform = run("uname", shell=False, pty=False)
    platform = c.run("uname", pty=False, echo=False, hide=True)
    if platform in ('NetBSD', 'OpenBSD', 'QNX'):
        # Attempt to protect against failures/collisions
        hasher = hashlib.sha1()
        hasher.update(c.host_string) # TODO: what did env.host_string become?
        hasher.update(filename)
        context['tmp'] = "/tmp/%s" % hasher.hexdigest()
        # Use temp file to work around lack of -i
        expr = r"""cp -p %(filename)s %(tmp)s \
&& sed -r -e %(script)s %(filename)s > %(tmp)s \
&& cp -p %(filename)s %(filename)s%(backup)s \
&& mv %(tmp)s %(filename)s"""
    else:
        context['extended_regex'] = '-E' if platform == 'Darwin' else '-r'
        expr = r"sed -i%(backup)s %(extended_regex)s -e %(script)s %(filename)s"
    command = expr % context
    return func(command,
                # shell=shell
    )


def uncomment(c, filename, regex, use_sudo=False, char='#', backup='.bak',
    # shell=False,
):
    """
    NOTE: This was copied from the upstream ``fabric.contrib.files`` (v1) module.

    Attempt to uncomment all lines in ``filename`` matching ``regex``.

    The default comment delimiter is `#` and may be overridden by the ``char``
    argument.

    This function uses the `sed` function, and will accept the same
    ``use_sudo``, ``shell`` and ``backup`` keyword arguments that `sed` does.

    `uncomment` will remove a single whitespace character following the comment
    character, if it exists, but will preserve all preceding whitespace.  For
    example, ``# foo`` would become ``foo`` (the single space is stripped) but
    ``    # foo`` would become ``    foo`` (the single space is still stripped,
    but the preceding 4 spaces are not.)

    .. versionchanged:: 1.6
        Added the ``shell`` keyword argument.
    """
    return sed(
        c,
        filename,
        before=r'^([[:space:]]*)%s[[:space:]]?' % char,
        after=r'\1',
        limit=regex,
        use_sudo=use_sudo,
        backup=backup,
        # shell=shell
    )
