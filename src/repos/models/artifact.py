#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import appier
import appier_extras

from . import package

class Artifact(appier_extras.admin.Base):

    version = appier.field(
        index = True,
        default = True,
        immutable = True
    )

    path = appier.field(
        index = True
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
            appier.not_null("version"),
            appier.not_empty("version")
        ]

    @classmethod
    def list_names(cls):
        return ["version", "package", "description"]

    @classmethod
    def retrieve(cls, name, version = None):
        kwargs = dict()
        if version: kwargs["version"] = version
        artifact = Artifact.get(name, **kwargs)
        file = open(artifact.path, "rb")
        try: contents = file.read()
        finally: file.close()
        return contents

    @classmethod
    def publish(cls, name, version, data):
        artifact = Artifact.get(name, version = version, raise_e = False)
        if artifact: raise appier.OperationalError(message = "Duplicated artifact")
        path = cls.store(name, version, data)
        _package = package.Package.get(name = name, raise_e = False)
        if not _package:
            _package = package.Package(name = name)
            _package.save()
        artifcat = Artifact(version = version, path = path, package = _package)
        artifcat.save()

    @classmethod
    def store(cls, name, version, data):
        BASE_PATH = "c:/repo" # @todo must be env variable
        base_path = os.path.join(BASE_PATH, name)
        file_path = os.path.join(base_path, version + ".cpx")
        base_path = os.path.normpath(base_path)
        file_path = os.path.normpath(file_path)
        if not os.path.exists(base_path): os.makedirs(base_path)
        file = open(file_path, "wb")
        try: file.write(data)
        finally: file.close()
        return file_path
