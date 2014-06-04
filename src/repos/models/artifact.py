#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import appier_extras

class Artifact(appier_extras.admin.Base):

    version = appier.field(
        index = True,
        immutable = True
    )

    description = appier.field()

    package = appier.field(
        type = appier.reference(
            "Package",
            name = "name"
        )
    )

    @classmethod
    def validate(cls):
        return super(Artifact, cls).validate() + [
            appier.not_null("version"),
            appier.not_empty("version")
        ]
