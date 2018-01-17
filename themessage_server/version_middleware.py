from aiohttp import web


@web.middleware
async def version_middleware(request, handler):
    resp = await handler(request)
    # TODO: should get from themessage_server.__version__
    resp.headers['X-VERSION'] = '0.0.1'
    return resp
