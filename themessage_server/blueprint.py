"""
Inspired by Flask Blueprints
is used for scaffolding web application

# Features:

- modular - each blueprint has it own url prefix
- decorators - declarative describe url right near handler

"""

from aiohttp import web
import asyncio


class Blueprint:
    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path
        self.routers = []
        self.children = []

    def get(self, url):
        """
        handle GET method
        :param url:
        :return:
        """
        return self._route('get', url)

    def route(self, url):
        # TODO: should receive any method
        return self._route('get', url)

    def _parse_response(self, res):
        if isinstance(res, dict):
            return web.json_response(res)
        elif isinstance(res, str):
            return web.Response(body=res)
        elif isinstance(res, tuple):
            new_res = self._parse_response(res[0])
            new_res.state = res[1]
            return new_res
        else:
            return res

    def _route(self, method, url):
        def wrapper(fn):
            async def common_handler(request):
                res = fn(request)
                if asyncio.iscoroutine(res):
                    res = await res
                return self._parse_response(res)

            self.routers.append({
                'method': method,
                'url': url,
                'handler': common_handler,
            })
            return fn

        return wrapper

    def register_app(self, app, prefix=''):
        """
        Registered blueprint in aiohttp web app

        :param app:
        :param prefix:
        :return:
        """
        for r in self.routers:
            app.router.add_route(r['method'], prefix + r['url'], r['handler'])

        for c in self.children:
            c['child'].register_app(app, prefix=c['url_prefix'])

    def register_blueprint(self, child, url_prefix):
        """
        Register blueprint in parent blueprint

        :param child:
        :param url_prefix:
        :return:
        """
        self.children.append({
            'url_prefix': url_prefix,
            'child': child,
        })
