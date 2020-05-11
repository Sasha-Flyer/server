import psutil
import system_pb2
from aiohttp import web, ClientTimeout
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
    ws = web.WebSocketResponse(timeout=ClientTimeout(sock_read=10))
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

def run_server():
    try:
        print("Введите порт, который будет прослушивать этот сервер для отправки данных о загруженности")
        port = int(input())
        web.run_app(app, port=port)
    except OSError:
        print("Система уже прослушивает выбранный порт. Перезапустите приложение и попробуйте указать другой порт")
        input()

if __name__ == '__main__':
    run_server()

