import psutil
import system_pb2
from aiohttp import web, ClientTimeout
from asyncio import sleep, ensure_future

client_count = 0


def get_sys_info():
    system = system_pb2.SysMessage()
    system.type = "SYS_MESSAGE"
    memory_data = psutil.virtual_memory()
    system.used_memory = memory_data.used
    system.total_memory = memory_data.total
    system.cpu_usage = psutil.cpu_percent(0)
    system.ssd_usage = psutil.disk_usage('/').percent
    return system.SerializeToString()

async def reader(ws):
    async for msg in ws: pass

async def websocket_handler(request):
    global client_count
    client_count += 1
    print("клиент подключился, всего клиентов: {0}".format(client_count))
    ws = web.WebSocketResponse(timeout=ClientTimeout(sock_read=10))
    await ws.prepare(request)
    ensure_future(reader(ws))
    try:
        while True:
            info = get_sys_info()
            await ws.send_bytes(info)
            await sleep(1)
            if ws.closed:
                break
        return ws
    finally:
        client_count -= 1
        print("клиент отключился, всего клиентов: {0}".format(client_count))

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

