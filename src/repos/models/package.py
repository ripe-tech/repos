#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import appier_extras

class Package(appier_extras.admin.Base):
    """
    Top level entity that identifies a unique object
    in the system and that "contains" multiple artifacts
    representing multiple versions of the same package.
    """

    name = appier.field(
        index = True,
        default = True,
        immutable = True
    )
    """ The human readable name of the package that should
    also identify it unequivocally """

    identifier = appier.field(
        index = True,
        immutable = True
    )
    """ A technical name of the package, that should identify
    univocally this artifact, not meant to be readable """

    type = appier.field(
        index = True
    )
    """ The kind of package represented, different values
    may impose different interpretations by the client """

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
        return ["name", "identifier", "type", "description"]

    @appier.link(name = "Retrieve")
    def retrieve_url(self, absolute = False):
        return self.owner.url_for(
            "package.retrieve",
            name = self.name,
            absolute = absolute
        )

    @appier.view(name = "Artifacts")
    def artifacts_v(self, *args, **kwargs):
        from . import artifact
        kwargs["sort"] = kwargs.get("sort", [("created", -1)])
        kwargs.update(package = self.name)
        return appier.lazy_dict(
            model = artifact.Artifact,
            kwargs = kwargs,
            entities = appier.lazy(lambda: artifact.Artifact.find(*args, **kwargs)),
            page = appier.lazy(lambda: artifact.Artifact.paginate(*args, **kwargs)),
            names = ["id", "version", "created"]
        )
