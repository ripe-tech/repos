#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

import appier

import repos

class PackageController(appier.Controller):

    @appier.route("/packages", "GET", json = True)
    def list(self):
        self.ensure_auth()
        fields = self.fields()
        packages = repos.Package.find(map = True, **fields)
        return packages

    @appier.route("/packages/<str:name>", "GET", json = True)
    def retrieve(self, name):
        self.ensure_auth()
        version = self.field("version")
        data = repos.Artifact.retrieve(name = name, version = version)
        self.content_type("application/colony")
        return data

    @appier.route("/packages", "POST", json = True)
    @appier.ensure(token = "admin")
    def publish(self):
        id = self.field("id")
        name = self.field("name")
        version = self.field("version")
        contents = self.field("contents")
        info = self.field("info")
        type = self.field("type")
        if info: info = json.loads(info)
        _name, _content_type, data = contents
        repos.Artifact.publish(
            id,
            name,
            version,
            data,
            info = info,
            type = type
        )

    @appier.route("/packages/<str:name>/info", "GET", json = True)
    def info(self, name):
        version = self.field("version")
        return repos.Artifact._info(name = name, version = version)

    def ensure_auth(self):
        username = appier.conf("REPO_USERNAME", None)
        password = appier.conf("REPO_PASSWORD", None)
        if not username: return
        authorization = self.request.authorization
        is_valid = tuple(authorization) == (username, password)
        if not is_valid: raise appier.SecurityError(
            message = "Authentication failed",
            code = 401,
            headers = {
                "WWW-Authenticate" : "Basic realm=\"default\""
            }
        )
