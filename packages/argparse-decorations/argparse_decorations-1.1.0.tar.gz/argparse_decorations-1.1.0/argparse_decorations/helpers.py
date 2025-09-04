# -*- coding: utf-8 -*-
import datetime
from importlib import resources
import json
import pathlib
import subprocess


class BuildHelper(object):

    def __init__(self, package):
        self.package = package

    def update_dynamic_metadata(self):
        data = self._load_dynamic_metadata()
        with open(self._file('__metadata_dynamic__.json'), 'w+') as f:
            raw = json.dumps(data, indent=4)
            f.write(raw)

    def _file(self, filename):
        return pathlib.Path(self.package).joinpath(filename)

    def _load_dynamic_metadata(self):
        commit_hash = self._git('log --max-count 1 --pretty=format:%h',
                                'Cant get hash information')[0]

        branch = self._git('branch --show-current',
                           'Cant get branch information')[0]

        branchs = [b[2:] for b in self._git('branch --list --no-color '
                                            + '--merged', 'Cant get branch '
                                            + 'list information')
                   if b != '' and not b.startswith('* ')]

        tags = [t for t in self._git('tag --merged', 'Cant get tag list '
                                     + 'information')
                if t != '']

        return {
                'commit_hash': commit_hash,
                'compile_timestamp': self._get_compile_time_stamp(),
                'branch': branch,
                'branchs': branchs,
                'tags': tags,
                }

    def _git(self, command, error_message):
        proc = subprocess.run(['git'] + command.split(' '),
                              stdout=subprocess.PIPE)

        if proc.returncode != 0:
            raise Exception(error_message)

        return proc.stdout.decode().split('\n')

    def _get_compile_time_stamp(self):
        return datetime.datetime.now().strftime('%Y-%m-%d@%H:%M:%S.%f')

    def get_version(self):
        with open(self._file('__metadata_static__.json')) as f:
            version = json.loads(f.read())
            return '{major}.{minor}.{patch}'.format(**version)

    def get_metadata_files(self):
        _files = [self._file('__metadata_static__.json'),
                  self._file('__metadata_dynamic__.json')]
        return [('metadata', _files)]


class Metadata(object):

    def __init__(self, package):
        self.package = package

    def load_static(self):
        return self._load('__metadata_static__.json')

    def load_dynamic(self):
        return self._load('__metadata_dynamic__.json')

    def _load(self, filename):
        file = self._file(filename)
        contents = file.read_text()

        return json.loads(contents)

    def _file(self, file):
        return resources.files(self.package).joinpath(file)

    def load(self):
        static = self.load_static()

        static.update(self.load_dynamic())

        return static
