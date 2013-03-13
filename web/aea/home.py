#!/usr/bin/env python

import markdown
import os.path
import re
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import tornado.autoreload

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="blog database host")
define("mysql_database", default="blog", help="blog database name")
define("mysql_user", default="blog", help="blog database user")
define("mysql_password", default="blog", help="blog database password")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [ 
            (r"/", HomeHandler),
            (r"/myadd",MyAddHandler),
            (r"/detail",MyDetailHandler),
            (r"/chain",ChainHandler),
        ]
        settings = dict(
            blog_title="Anjuke_Expense_Applying",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Entry": EntryModule},
            #xsrf_cookies=True,
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
        debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class HomeHandler(BaseHandler):
    def get(self):
        entries = "This is Tornado Web";
        if not entries:
            self.redirect("/compose")
            return
        self.render("home.html", entries=entries)

class MyAddHandler(BaseHandler):
    def get(self):
        self.render("myadd.html")

class MyDetailHandler(BaseHandler):
    def get(self):
        self.render("mydetail.html")

class ChainHandler(BaseHandler):
    def get(self):
        self.render("chain.html")

class EntryModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/entry.html", entry=entry)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()
    #tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
