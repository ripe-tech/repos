#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

import appier

import repos

class PackageController(appier.Controller):

    @appier.route("/packages", "GET", json = True)
    def list(self):
        self.ensure_auth()
        object = appier.get_object(alias = True, find = True)
        packages = repos.Package.find(map = True, **object)
        return packages

    @appier.route("/packages/<str:name>", "GET", json = True)
    def retrieve(self, name):
        self.ensure_auth()
        version = self.field("version")
        data, content_type = repos.Artifact.retrieve(name = name, version = version)
        appier.verify(
            data == None,
            message = "No data available in the package",
            exception = appier.OperationalError
        )
        self.content_type(content_type or "application/octet-stream")
        return data

    @appier.route("/packages", "POST", json = True)
    @appier.ensure(token = "admin")
    def publish(self):
        identifier = self.field("identifier")
        name = self.field("name")
        version = self.field("version")
        contents = self.field("contents")
        info = self.field("info")
        type = self.field("type")
        content_type = self.field("content_type")
        if info: info = json.loads(info)
        _name, _content_type, data = contents
        repos.Artifact.publish(
            identifier,
            name,
            version,
            data,
            info = info,
            type = type,
            content_type = content_type
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
        is_valid = authorization == (username, password)
        if not is_valid: raise appier.SecurityError(
            message = "Authentication failed",
            code = 401,
            headers = {
                "WWW-Authenticate" : "Basic realm=\"default\""
            }
        )
