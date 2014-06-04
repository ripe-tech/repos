#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import appier_extras

from . import repo

class Package(appier_extras.admin.Base):

    name = appier.field(
        index = True,
        default = True,
        immutable = True
    )

    repo = appier.field(
        type = appier.reference(
            repo.Repo,
            name = "name"
        )
    )

    @classmethod
    def validate(cls):
        return super(Package, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
            appier.not_duplicate("name", cls._name())
        ]

    @classmethod
    def list_names(cls):
        return ["name", "repo", "description"]
