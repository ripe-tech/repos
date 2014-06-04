#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

import repos

class BaseController(appier.Controller):

    @appier.route("/artifacts/<str:name>", "GET")
    def retrieve(self, name):
        version = self.field("version")
        data = repos.Artifact.retrieve(name, version = version)
        self.content_type("application/colony")
        return data

    @appier.route("/artifacts/<str:name>", "POST")
    #@appier.ensure(token = "admin")
    def publish(self, name):
        version = self.field("version")
        contents = self.field("contents")
        _name, _content_type, data = contents
        repos.Artifact.publish(name, version, data)
