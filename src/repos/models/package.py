#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import appier_extras

class Package(appier_extras.admin.Base):

    identifier = appier.field(
        index = True,
        default = True,
        immutable = True
    )

    name = appier.field(
        index = True,
        immutable = True
    )

    type = appier.field(
        index = True
    )

    @classmethod
    def validate(cls):
        return super(Package, cls).validate() + [
            appier.not_null("identifier"),
            appier.not_empty("identifier"),
            appier.not_duplicate("identifier", cls._name()),

            appier.not_null("name"),
            appier.not_empty("name"),
            appier.not_duplicate("name", cls._name())
        ]

    @classmethod
    def list_names(cls):
        return ["name", "description"]
