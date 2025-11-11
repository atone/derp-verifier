import json
import asyncio
from aiohttp import web


def colorize(text, color):
    code = f"\033[{color}m"
    restore = "\033[0m"
    return "".join([code, text, restore])


def make_log(level: str, msg: str) -> str:
    if level == "warning":
        prefix = colorize("[Warn]", "1;31")
    elif level == "info":
        prefix = colorize("[Info]", "1;34")
    elif level == "error":
        prefix = colorize("[Err ]", "1;31")
    else:
        raise ValueError(f"Unknown level {level}")
    return prefix + " " + msg


def log(level: str, msg: str) -> None:
    """Log something with a given level."""
    print(make_log(level, msg))


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


def deny_response() -> web.Response:
    return web.Response(text="404: Not Found", status=404)


async def verify_handler(request: web.Request) -> web.Response:
    if request.method != 'POST':
        return deny_response()

    try:
        data = await request.json()
    except Exception:
        return deny_response()

    if not isinstance(data, dict):
        return deny_response()

    if 'NodePublic' not in data or 'Source' not in data:
        return deny_response()

    node_public = data['NodePublic']
    source = data['Source']

    public_keys = await get_public_keys()

    if node_public in public_keys:
        log("info", f"Allowing access for NodePublic: {node_public}, Source: {source}")
        return web.json_response({'Allow': True})

    log("warning", f"Denying access for NodePublic: {node_public}, Source: {source}")
    return web.json_response({'Allow': False})


def init_app() -> web.Application:
    app = web.Application()
    app.router.add_route('*', '/verify', verify_handler)
    return app


if __name__ == '__main__':
    app = init_app()
    web.run_app(app, host='0.0.0.0', port=8080)
