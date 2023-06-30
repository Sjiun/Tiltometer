
import asyncio
import websockets
import json

CLIENTS = {}
FRONTEND_CLIENT = 0
# documentation: https://websockets.readthedocs.io/en/stable/index.html



async def handler(websocket):
    # clients.append(websocket)
    # TODO: only add frontend to open sockets!
    # keep websockets open
    while True:
        try:
            dataString = await websocket.recv()
        except websockets.ConnectionClosed:
            print(f"Terminated")
            break

        

        if(dataString=="FRONTEND"):
            print(' - add frontend')
            CLIENTS[FRONTEND_CLIENT] = websocket
            print(' - added frontend')
        else :
            print(f'--- {dataString}')
            data = json.loads(dataString)
            # print(data)
            
            # data = await websocket.recv()
            # print(f"ON-SERVER received: {data}")
            print(f"ON-SERVER received: {data['data']}")

            response = f"back - {data['data']}!"

            await websocket.send(response)
            print(f"ON-SERVER responded: {response}")

            # TODO: broadcast only to frontend
            # if(CLIENTS[FRONTEND_CLIENT]):
            if(len(CLIENTS) > 0):
                print('ON-SERVER: send to frontend')
                # await CLIENTS[FRONTEND_CLIENT].send('HELLO FRONTEND!!!')
                await CLIENTS[FRONTEND_CLIENT].send(str(data['data']))
                
            # print(f" - clients: {len(CLIENTS)}")

async def main():
    # `0.0.0.0` so that socket is also available on local machine for overwolf
    async with websockets.serve(handler, "0.0.0.0", 5000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())