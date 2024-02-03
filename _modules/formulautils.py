# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals

import logging
from pathlib import Path

# Import Salt libs
from salt.exceptions import CommandExecutionError

log = logging.getLogger(__name__)


def file_switch(
    source_files,
    tpldir,
    lookup=None,
    default_files_switch=None,
    indent_width=6,
    use_subpath=False,
):
    """
    Returns a valid value for the "source" parameter of a "file.managed"
    state function. This makes easier the usage of the Template Override and
    Files Switch (TOFS) pattern.
    Params:
      * source_files: ordered list of files to look for
      * lookup: key under "<tplroot>:tofs:source_files" to prepend to the
        list of source files
      * default_files_switch: if there's no config (e.g. pillar)
        "<tplroot>:tofs:files_switch" this is the ordered list of grains to
        use as selector switch of the directories under
        "<path_prefix>/files"
      * indent_width: indentation of the result value to conform to YAML
      * use_subpath: defaults to `False` but if set, lookup the source file
        recursively from the current state directory up to `tplroot`
    Example (based on a `tplroot` of `xxx`):
    If we have a state:
      Deploy configuration:
        file.managed:
          - name: /etc/yyy/zzz.conf
          - source: {{ salt['formulautils.files_switch'](
                         ["/etc/yyy/zzz.conf", "/etc/yyy/zzz.conf.jinja"],
                         lookup="Deploy configuration",
                       ) }}
          - template: jinja
    In a minion with id=theminion and os_family=RedHat, it's going to be
    rendered as:
      Deploy configuration:
        file.managed:
          - name: /etc/yyy/zzz.conf
          - source:
            - salt://xxx/files/theminion/etc/yyy/zzz.conf
            - salt://xxx/files/theminion/etc/yyy/zzz.conf.jinja
            - salt://xxx/files/RedHat/etc/yyy/zzz.conf
            - salt://xxx/files/RedHat/etc/yyy/zzz.conf.jinja
            - salt://xxx/files/default/etc/yyy/zzz.conf
            - salt://xxx/files/default/etc/yyy/zzz.conf.jinja
          - template: jinja

    """
    tpldir = Path(tpldir)
    source_files = source_files if isinstance(source_files, list) else [source_files]
    tplroot = Path(tpldir.parts[0])
    path_prefix = Path(__salt__['config.get'](f'{tplroot}:tofs:path_prefix', tplroot))
    files_dir = __salt__['config.get'](f'{tplroot}:tofs:dirs:files', 'files')
    files_switch_list = __salt__['config.get']('f{tplroot}:tofs:files_switch',
            default_files_switch if default_files_switch is not None else ['id', 'os_family'])
    src_files = __salt__['config.get'](f'{tplroot}:tofs:source_files:{lookup}',
                                       __salt__['config.get'](f'{tplroot}:tofs:files:{lookup}', []))
    src_files.extend(source_files)
    subpaths = [path_prefix]
    if use_subpath and tplroot != tpldir:
        for path in tpldir.parts[1:]:
            subpaths.append(subpaths[-1] / path)
        subpaths.reverse()
    urls = []
    for subpath in subpaths:
        for file_switch_target in files_switch_list:
            fls = __salt__['config.get'](file_switch_target)
            if isinstance(fls, str):
                fls = [fls]
            for fl_ in fls:
                for src_file in src_files:
                    urls.append(subpath / files_dir / fl_ / src_file)
        for src_file in src_files:
            urls.append(subpath / files_dir / "default" / src_file)
    data = ''
    for url in urls:
        data += f'{" " * indent_width}{str(url)}\n'
    return data
