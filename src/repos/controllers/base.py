#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

class BaseController(appier.Controller):
    
    @appier.route("/artifacts", "POST")
    #@appier.ensure(token = "admin")
    def create_artifact(self):
        name = self.field("name")
        version = self.field("version")
        contents = self.field("contents")
        print name
        print version
        print contents