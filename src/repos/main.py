#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import appier_extras

class ReposApp(appier.WebApp):

    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(
            self,
            name = "repos",
            parts = (
                appier_extras.AdminPart,
            ),
            *args, **kwargs
        )

if __name__ == "__main__":
    app = ReposApp()
    app.serve()
else:
    __path__ = []
