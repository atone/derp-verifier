import json
import asyncio
import logging
from aiohttp import web

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def get_tailscale_status():
    process = await asyncio.create_subprocess_exec(
        'tailscale', 'status', '--json',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"tailscale command failed: {stderr.decode()}")

    return json.loads(stdout)


async def get_public_keys():
    status = await get_tailscale_status()
    public_keys = []

    if 'Self' in status and 'PublicKey' in status['Self']:
        public_keys.append(status['Self']['PublicKey'])

    for node in status.get('Peer', {}).values():
        if 'PublicKey' in node:
            public_keys.append(node['PublicKey'])

    return public_keys


async def verify_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=404)

    if not isinstance(data, dict):
        return web.Response(status=404)
    if 'NodePublic' not in data or 'Source' not in data:
        return web.Response(status=404)

    node_public = data['NodePublic']
    source = data['Source']

    public_keys = await get_public_keys()
    if node_public in public_keys:
        log.info(f"Allowing access for NodePublic: {node_public}, Source: {source}")
        return web.json_response({'Allow': True})
    log.warning(f"Denying access for NodePublic: {node_public}, Source: {source}")
    return web.json_response({'Allow': False})


def init_app() -> web.Application:
    app = web.Application()
    app.router.add_post('/verify', verify_handler)
    return app


if __name__ == '__main__':
    app = init_app()
    web.run_app(app, host='0.0.0.0', port=8080)
