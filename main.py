import psutil
import system_pb2
from aiohttp import web
from asyncio import sleep


def get_sys_info():
    system = system_pb2.SysMessage()
    system.type = "SYS_MESSAGE"
    memory_data = psutil.virtual_memory()
    system.used_memory = memory_data.used
    system.total_memory = memory_data.total
    system.cpu_usage = psutil.cpu_percent(0)
    system.ssd_usage = psutil.disk_usage('/').percent
    return system.SerializeToString()


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    while True:
        info = get_sys_info()
        await ws.send_bytes(info)
        await sleep(1)
        if ws.closed:
            break
    return ws

app = web.Application()
app.add_routes([web.get('/', websocket_handler)])

if __name__ == '__main__':
    web.run_app(app)

