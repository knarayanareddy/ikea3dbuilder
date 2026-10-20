import asyncio, json, urllib.request, websockets, sys, time

async def test_kit(kit_name):
    url = f"http://localhost:8002/viewer/index.html#{kit_name}"
    req = urllib.request.Request(f'http://localhost:9222/json/new?{url}', method='PUT')
    tab = json.loads(urllib.request.urlopen(req).read().decode())
    ws_url = tab['webSocketDebuggerUrl']
    tab_id = tab['id']

    seq = 0
    futures = {}
    exceptions = []

    async def send_cmd(ws, method, params=None):
        nonlocal seq
        seq += 1
        mid = seq
        fut = asyncio.get_running_loop().create_future()
        futures[mid] = fut
        req_data = {'id': mid, 'method': method}
        if params: req_data['params'] = params
        await ws.send(json.dumps(req_data))
        try:
            return await asyncio.wait_for(fut, timeout=6.0)
        except asyncio.TimeoutError:
            print(f"[{kit_name}] Timeout waiting for {method} (id={mid})", flush=True)
            return None

    try:
        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            async def reader():
                try:
                    while True:
                        raw = await ws.recv()
                        msg = json.loads(raw)
                        mid = msg.get('id')
                        if mid is not None and mid in futures and not futures[mid].done():
                            futures[mid].set_result(msg)
                        elif msg.get('method') == 'Runtime.exceptionThrown':
                            ex = msg['params']['exceptionDetails']
                            print(f'[{kit_name}] EXCEPTION:', ex.get('text'), ex.get('exception', {}).get('description'), flush=True)
                            exceptions.append(ex)
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"[{kit_name}] Reader error:", e, flush=True)

            t = asyncio.create_task(reader())
            await send_cmd(ws, 'Runtime.enable')
            await send_cmd(ws, 'Page.enable')

            # Wait for load and first frame
            await asyncio.sleep(2.5)

            # Evaluate state
            res = await send_cmd(ws, 'Runtime.evaluate', {
                'expression': 'JSON.stringify({kit: ie.id, title: ie.title, N: K, dbg: window.__dbg ? window.__dbg() : null})'
            })
            val = res.get('result', {}).get('result', {}).get('value') if res else None
            print(f"[{kit_name.upper()}] BOOT RESULT: {val}", flush=True)

            # Test advancing to Step 1
            await send_cmd(ws, 'Runtime.evaluate', {'expression': 'window.__lab.at(1)'})
            await asyncio.sleep(0.5)
            res_step1 = await send_cmd(ws, 'Runtime.evaluate', {
                'expression': 'JSON.stringify({step: window.__dbg ? window.__dbg().step : -1, text: document.getElementById("st-title").textContent})'
            })
            val_s1 = res_step1.get('result', {}).get('result', {}).get('value') if res_step1 else None
            print(f"[{kit_name.upper()}] STEP 1 RESULT: {val_s1}", flush=True)

            t.cancel()
    finally:
        try:
            urllib.request.urlopen(f'http://localhost:9222/json/close/{tab_id}')
        except:
            pass

    return len(exceptions) == 0 and val is not None

async def main():
    results = {}
    for kit in ['billy', 'lack', 'marius', 'gladom']:
        print(f"\n--- Testing {kit.upper()} ---", flush=True)
        ok = await test_kit(kit)
        results[kit] = ok

    print("\n================ SUMMARY ================", flush=True)
    all_ok = True
    for kit, ok in results.items():
        print(f"Kit {kit.upper()}: {'PASSED' if ok else 'FAILED'}")
        if not ok: all_ok = False
    print("=========================================\n", flush=True)
    if not all_ok:
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
