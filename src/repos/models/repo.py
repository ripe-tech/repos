#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import appier_extras

class Repo(appier_extras.admin.Base):

    name = appier.field(
        index = True,
        default = True,
        immutable = True
    )

    @classmethod
    def validate(cls):
        return super(Repo, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
            appier.not_duplicate("name", cls._name())
        ]

    @classmethod
    def list_names(cls):
        return ["name", "description"]
