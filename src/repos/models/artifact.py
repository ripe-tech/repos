#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import shutil
import zipfile
import tempfile

import appier
import appier_extras

from . import package

class Artifact(appier_extras.admin.Base):

    identifier = appier.field(
        index = True,
        default = True,
        immutable = True
    )

    version = appier.field(
        index = True,
        default = True,
        immutable = True
    )

    info = appier.field(
        type = dict,
        private = True
    )

    path = appier.field(
        index = True,
        private = True
    )

    package = appier.field(
        type = appier.reference(
            package.Package,
            name = "name"
        )
    )

    @classmethod
    def validate(cls):
        return super(Artifact, cls).validate() + [
            appier.not_null("identifier"),
            appier.not_empty("identifier"),

            appier.not_null("version"),
            appier.not_empty("version")
        ]

    @classmethod
    def list_names(cls):
        return ["version", "package", "description"]

    @classmethod
    def retrieve(cls, identifier = None, name = None, version = None):
        kwargs = dict()
        if identifier: kwargs["identifier"] = identifier
        if name: kwargs["package"] = name
        if version: kwargs["version"] = version
        artifact = Artifact.get(rules = False, sort = [("version", -1)], **kwargs)
        contents = cls.read(artifact.path)
        return contents

    @classmethod
    def publish(
        cls,
        identifier,
        name,
        version,
        data,
        info = None,
        type = "package",
        replace = True
    ):
        artifact = Artifact.get(
            identifier = identifier,
            package = name,
            version = version,
            raise_e = False
        )
        if artifact and not replace:
            raise appier.OperationalError(message = "Duplicated artifact")
        if info: info["timestamp"] = time.time()
        _package = package.Package.get(identifier = identifier, name = name, raise_e = False)
        if not _package:
            _package = package.Package(
                identifier = identifier,
                name = name,
                type = type
            )
            _package.save()
        path = cls.store(name, version, data)
        artifact = artifact or Artifact(
            identifier = identifier,
            version = version,
            package = _package
        )
        artifact.info = info
        artifact.path = path
        artifact.save()

    @classmethod
    def store(cls, name, version, data):
        repo_path = appier.conf("REPO_PATH", "repo")
        base_path = os.path.join(repo_path, name)
        file_path = os.path.join(base_path, version)
        base_path = os.path.normpath(base_path)
        file_path = os.path.normpath(file_path)
        simple_path = "%s/%s" % (name, version)
        if not os.path.exists(base_path): os.makedirs(base_path)
        file = open(file_path, "wb")
        try: file.write(data)
        finally: file.close()
        return simple_path

    @classmethod
    def read(cls, path):
        repo_path = appier.conf("REPO_PATH", "repo")
        full_path = os.path.join(repo_path, path)
        full_path = os.path.normpath(full_path)
        file = open(full_path, "rb")
        try: contents = file.read()
        finally: file.close()
        return contents

    @classmethod
    def compress(cls):
        repo_path = appier.conf("REPO_PATH", "repo")
        _zip_handle, zip_path = tempfile.mkstemp()
        zip_file = zipfile.ZipFile(zip_path, "w")
        try:
            for name, _subdirs, files in os.walk(repo_path):
                relative_name = os.path.relpath(name, repo_path)
                zip_file.write(name, relative_name)
                for filename in files:
                    file_path = os.path.join(name, filename)
                    relative_path = os.path.relpath(file_path, repo_path)
                    zip_file.write(file_path, relative_path)
        finally: zip_file.close()
        return zip_path

    @classmethod
    def expand(cls, zip_path, empty = True):
        repo_path = appier.conf("REPO_PATH", "repo")
        exists = os.path.exists(repo_path)
        if empty and exists: shutil.rmtree(repo_path); exists = False
        if not exists: os.makedirs(repo_path)
        zip_file = zipfile.ZipFile(zip_path, "r")
        try: zip_file.extractall(repo_path)
        finally: zip_file.close()

    @classmethod
    @appier.link(name = "Compress")
    def compress_url(cls, absolute = False):
        return appier.get_app().url_for(
            "base.compress",
            absolute = absolute
        )

    @classmethod
    @appier.operation(
        name = "Expand",
        parameters = (
            ("Zip File", "file", "file"),
            ("Empty source", "empty", bool, True)
        )
    )
    def expand_s(cls, file, empty):
        _file_name, _mime_type, data = file
        _handle, path = tempfile.mkstemp()
        file = open(path, "wb")
        try: file.write(data)
        finally: file.close()
        cls.expand(path, empty = empty)

    @classmethod
    def _info(cls, name, version = None):
        kwargs = dict()
        if version: kwargs["version"] = version
        artifact = Artifact.get(
            package = name,
            rules = False,
            sort = [("version", -1)],
            **kwargs
        )
        return artifact.info
