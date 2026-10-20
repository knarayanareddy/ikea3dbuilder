import asyncio, json, urllib.request, websockets, sys

async def main(url="http://localhost:8002/viewer/index.html"):
    req = urllib.request.Request(f'http://localhost:9222/json/new?{url}', method='PUT')
    tab = json.loads(urllib.request.urlopen(req).read().decode())
    ws_url = tab['webSocketDebuggerUrl']
    tab_id = tab['id']
    print(f"Opened tab {tab_id} at {url}")

    seq = 0
    futures = {}
    exceptions = []

    async def send_cmd(ws, method, params=None):
        nonlocal seq
        seq += 1
        msg_id = seq
        fut = asyncio.get_running_loop().create_future()
        futures[msg_id] = fut
        payload = {'id': msg_id, 'method': method}
        if params:
            payload['params'] = params
        print(f"-> SEND {method} (id={msg_id})")
        await ws.send(json.dumps(payload))
        return await fut

    try:
        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            async def reader():
                try:
                    while True:
                        raw = await ws.recv()
                        msg = json.loads(raw)
                        mid = msg.get('id')
                        if mid is not None:
                            print(f"<- RECV id={mid} (in futures: {mid in futures})")
                            if mid in futures:
                                futures[mid].set_result(msg)
                        elif msg.get('method') == 'Runtime.consoleAPICalled':
                            args = [str(a.get('value', '')) for a in msg['params'].get('args', [])]
                            print("[CONSOLE]", " ".join(args))
                        elif msg.get('method') == 'Runtime.exceptionThrown':
                            details = msg['params']['exceptionDetails']
                            print("[EXCEPTION]", details.get('text'), details.get('exception', {}).get('description'))
                            exceptions.append(details)
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    import traceback
                    traceback.print_exc()

            reader_task = asyncio.create_task(reader())

            await send_cmd(ws, 'Runtime.enable')
            await send_cmd(ws, 'Page.enable')

            print("Waiting 3s for WebGL initial boot...")
            await asyncio.sleep(3)

            for kit in ['billy', 'lack', 'marius', 'gladom']:
                if kit != 'billy':
                    await send_cmd(ws, 'Runtime.evaluate', {'expression': f'window.__lab.kit("{kit}")'})
                    await asyncio.sleep(1)

                eval_res = await send_cmd(ws, 'Runtime.evaluate', {
                    'expression': 'JSON.stringify({title: document.title, dbg: window.__dbg ? window.__dbg() : null})'
                })
                val = eval_res.get('result', {}).get('result', {}).get('value')
                print(f"[{kit.upper()}] status: {val}")

            reader_task.cancel()
    finally:
        urllib.request.urlopen(f'http://localhost:9222/json/close/{tab_id}')
        print("Closed tab")

    if exceptions:
        print(f"FAILED with {len(exceptions)} exceptions!")
        sys.exit(1)
    else:
        print("ALL 4 KITS TESTED CLEANLY WITH ZERO EXCEPTIONS!")

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8002/viewer/index.html"
    asyncio.run(main(url))
