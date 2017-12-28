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
    """
    The base unit for the management or a repository, should
    be an concrete based entity belonging to a package.
    """

    identifier = appier.field(
        index = True,
        default = True,
        immutable = True
    )
    """ A simple human readable value that should identify
    (not univocally) this artifact """

    version = appier.field(
        index = True,
        default = True,
        immutable = True
    )
    """ A simple string identifying the version of this artifact
    should be in the form of "x.x.x", "master", "stable" etc." """

    info = appier.field(
        type = dict,
        private = True
    )
    """ Dictionary that contains a series of meta-information about
    this artifact (eg: external URLs, description, timestamps, etc.) """

    path = appier.field(
        index = True,
        private = True
    )
    """ The file system path to the file where this artifact can be
    found, this may be empty if the artifact is an external one """

    content_type = appier.field(
        index = True,
        private = True
    )
    """ The field that describes the MIME based content type of the
    artifact, to be used in data retrieval """

    package = appier.field(
        type = appier.reference(
            package.Package,
            name = "name"
        )
    )
    """ Reference to the "parent" package to which this artifact
    belongs, if this value is not set the artifact is considered
    an "orphan" one """

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
        return ["package", "version", "content_type", "description"]

    @classmethod
    def retrieve(cls, identifier = None, name = None, version = None):
        kwargs = dict()
        if identifier: kwargs["identifier"] = identifier
        if name: kwargs["package"] = name
        if version: kwargs["version"] = version
        artifact = Artifact.get(rules = False, sort = [("version", -1)], **kwargs)
        contents = cls.read(artifact.path)
        content_type = artifact.content_type
        return contents, content_type

    @classmethod
    def publish(
        cls,
        identifier,
        name,
        version,
        data,
        info = None,
        type = "package",
        content_type = None,
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
        artifact.content_type = content_type
        artifact.save()
        return artifact

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
            ("Empty source", "empty", bool, False)
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
    @appier.operation(
        name = "Import",
        parameters = (
            ("Package", "package", str),
            ("Version", "version", str),
            ("File", "file", "file")
        ),
        factory = True
    )
    def import_s(cls, package, version, file):
        return cls.publish(
            package + "_" + version,
            package,
            version,
            file.read()
        )

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
