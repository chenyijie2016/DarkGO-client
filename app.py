#!/usr/bin/env python
# -*- coding: utf-8 -*-     
# Copyright (c) 2017 cyj <chenyijiethu@gmail.com>
# Date: 17-9-19

from flask import Flask
import flask_restful as restful

from DarkGo import DarkGO

app = Flask(__name__)
app.config["gamepool"] = {}
app.config["queuepool"] = {}
api = restful.Api(app)
api.add_resource(DarkGO, '/game')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6006, debug=True)
