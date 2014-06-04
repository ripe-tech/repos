#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

import appier

import repos

class ArtifactController(appier.Controller):

    @appier.route("/artifacts", "GET", json = True)
    def list(self):
        object = appier.get_object(alias = True, find = True)
        artifacts = repos.Artifact.find(map = True, **object)
        return artifacts

    @appier.route("/artifacts/<str:name>", "GET", json = True)
    def retrieve(self, name):
        version = self.field("version")
        data = repos.Artifact.retrieve(name, version = version)
        self.content_type("application/colony")
        return data

    @appier.route("/artifacts/<str:name>", "POST", json = True)
    #@appier.ensure(token = "admin")
    def publish(self, name):
        version = self.field("version")
        contents = self.field("contents")
        info = self.field("info")
        type = self.field("type")
        if info: info = json.loads(info)
        _name, _content_type, data = contents
        repos.Artifact.publish(name, version, data, info = info, type = type)

    @appier.route("/artifacts/<str:name>/info", "GET", json = True)
    def info(self, name):
        version = self.field("version")
        return repos.Artifact._info(name, version = version)
