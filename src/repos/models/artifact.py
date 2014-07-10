#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time

import appier
import appier_extras

from . import package

class Artifact(appier_extras.admin.Base):

    id = appier.field(
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
            appier.not_null("id"),
            appier.not_empty("id"),

            appier.not_null("version"),
            appier.not_empty("version")
        ]

    @classmethod
    def list_names(cls):
        return ["version", "package", "description"]

    @classmethod
    def retrieve(cls, id = None, name = None, version = None):
        kwargs = dict()
        if id: kwargs["id"] = id
        if name: kwargs["package"] = name
        if version: kwargs["version"] = version
        artifact = Artifact.get(rules = False, sort = [("version", -1)], **kwargs)
        file = open(artifact.path, "rb")
        try: contents = file.read()
        finally: file.close()
        return contents

    @classmethod
    def publish(
        cls,
        id,
        name,
        version,
        data,
        info = None,
        type = "package",
        replace = True
    ):
        artifact = Artifact.get(
            id = id,
            package = name,
            version = version,
            raise_e = False
        )
        if artifact and not replace:
            raise appier.OperationalError(message = "Duplicated artifact")
        if info: info["timestamp"] = time.time()
        _package = package.Package.get(id = id, name = name, raise_e = False)
        if not _package:
            _package = package.Package(
                id = id,
                name = name,
                type = type
            )
            _package.save()
        path = cls.store(name, version, data)
        artifact = artifact or Artifact(
            id = id,
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
        if not os.path.exists(base_path): os.makedirs(base_path)
        file = open(file_path, "wb")
        try: file.write(data)
        finally: file.close()
        return file_path

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
