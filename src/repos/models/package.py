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

    latest = appier.field(
        index = True,
        safe = True
    )
    """ The name/description of the latest artifact available
    for the this package """

    latest_timestamp = appier.field(
        type = int,
        index = "all",
        safe = True,
        meta = "datetime"
    )
    """ The date (and time) of when the last artifact related with
    this package has been made available """

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
        return ["name", "identifier", "type", "latest", "description"]

    def pre_save(self):
        appier_extras.admin.Base.pre_save(self)
        latest_artifact = self.latest_artifact
        if latest_artifact: self.latest_timestamp = latest_artifact.timestamp

    def pre_delete(self):
        appier_extras.admin.Base.pre_delete(self)
        from . import artifact
        artifacts = artifact.Artifact.find(package = self.name, limit = -1)
        for artifact in artifacts: artifact.delete()

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
        kwargs["sort"] = kwargs.get("sort", [("modified", -1)])
        kwargs.update(package = self.name)
        return appier.lazy_dict(
            model = artifact.Artifact,
            kwargs = kwargs,
            entities = appier.lazy(lambda: artifact.Artifact.find(*args, **kwargs)),
            page = appier.lazy(lambda: artifact.Artifact.paginate(*args, **kwargs)),
            names = ["id", "version", "branch", "timestamp"]
        )

    @property
    def latest_artifact(self):
        from . import artifact
        if not self.latest: return None
        if not self.name: return None
        return artifact.Artifact.get(
            version = self.latest,
            package = self.name,
            raise_e = False
        )
