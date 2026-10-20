import asyncio, json, urllib.request, websockets, sys, time, base64

async def snap_kit(kit_name, step=0):
    url = f"http://localhost:8002/viewer/index.html#{kit_name}"
    req = urllib.request.Request(f'http://localhost:9222/json/new?{url}', method='PUT')
    tab = json.loads(urllib.request.urlopen(req).read().decode())
    ws_url = tab['webSocketDebuggerUrl']
    tab_id = tab['id']

    seq = 0
    futures = {}

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
        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            async def reader():
                try:
                    while True:
                        raw = await ws.recv()
                        msg = json.loads(raw)
                        mid = msg.get('id')
                        if mid is not None and mid in futures and not futures[mid].done():
                            futures[mid].set_result(msg)
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"[{kit_name}] Reader error:", e, flush=True)

            t = asyncio.create_task(reader())
            await send_cmd(ws, 'Runtime.enable')
            await send_cmd(ws, 'Page.enable')

            # Wait for load and first frame
            await asyncio.sleep(2.5)

            # Switch step if needed
            if step > 0:
                await send_cmd(ws, 'Runtime.evaluate', {'expression': f'window.__lab.at({step})'})
                await asyncio.sleep(1.0)

            # Capture using window.__capture()
            eval_res = await send_cmd(ws, 'Runtime.evaluate', {
                'expression': 'window.__capture(1400, 0.9)',
                'returnByValue': True
            })
            val = eval_res.get('result', {}).get('result', {}).get('value') if eval_res else None
            if val and val.startswith('data:image'):
                b64 = val.split(',', 1)[1]
                out_path = f"/Users/brightech/Downloads/ikea/flatpack/shot_{kit_name}_step{step}.webp"
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(b64))
                print(f"SUCCESS: Saved {out_path} ({len(b64)} chars)", flush=True)
            else:
                print(f"FAILED to capture {kit_name} step {step}, eval returned: {val[:80] if val else None}", flush=True)

            t.cancel()
    finally:
        try:
            urllib.request.urlopen(f'http://localhost:9222/json/close/{tab_id}')
        except:
            pass

async def main():
    for kit in ["marius", "gladom"]:
        for s in [0, 1, 2, 3]:
            print(f"Snapping {kit} step {s}...", flush=True)
            await snap_kit(kit, s)

if __name__ == '__main__':
    asyncio.run(main())
