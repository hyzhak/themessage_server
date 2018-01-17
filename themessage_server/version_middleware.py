from aiohttp import web
import themessage_server


@web.middleware
async def version_middleware(request, handler):
    resp = await handler(request)
    resp.headers['X-VERSION'] = themessage_server.__version__
    return resp
