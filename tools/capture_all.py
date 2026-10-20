import asyncio, json, urllib.request, websockets, sys, time, base64
from PIL import Image
import numpy as np

async def capture_all_kits():
    for kit in ["billy", "lack", "marius", "gladom"]:
        url = f"http://localhost:8002/viewer/index.html#{kit}"
        req = urllib.request.Request(f'http://localhost:9222/json/new?{url}', method='PUT')
        tab = json.loads(urllib.request.urlopen(req).read().decode())
        ws_url = tab['webSocketDebuggerUrl']
        tab_id = tab['id']

        seq = 0
        futures = {}

        async def send(ws, method, params=None):
            nonlocal seq
            seq += 1
            mid = seq
            fut = asyncio.get_running_loop().create_future()
            futures[mid] = fut
            p = {'id': mid, 'method': method}
            if params: p['params'] = params
            await ws.send(json.dumps(p))
            return await fut

        try:
            async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
                async def reader():
                    try:
                        while True:
                            msg = json.loads(await ws.recv())
                            mid = msg.get('id')
                            if mid is not None and mid in futures and not futures[mid].done():
                                futures[mid].set_result(msg)
                    except: pass

                t = asyncio.create_task(reader())
                await send(ws, 'Runtime.enable')
                await asyncio.sleep(2.5)

                # Get kit steps count
                res_N = await send(ws, 'Runtime.evaluate', {'expression': 'ie.N', 'returnByValue': True})
                N = res_N.get('result', {}).get('result', {}).get('value', 3)
                print(f"=== {kit.upper()} (N={N}) ===")

                for step in range(N + 1):
                    # Set step
                    await send(ws, 'Runtime.evaluate', {'expression': f'window.__lab.at({step})'})
                    await asyncio.sleep(0.6)

                    # Render and capture
                    code = "(() => { window.__step(performance.now()); return window.__capture(1400, 0.9); })()"
                    res = await send(ws, 'Runtime.evaluate', {'expression': code, 'returnByValue': True})
                    val = res.get('result', {}).get('result', {}).get('value')
                    if val and val.startswith('data:image'):
                        b64 = val.split(',', 1)[1]
                        raw = base64.b64decode(b64)
                        out_path = f"/Users/brightech/Downloads/ikea/flatpack/shot_{kit}_step{step}.png"
                        # Convert webp to png
                        import io
                        im = Image.open(io.BytesIO(raw))
                        im.save(out_path, "PNG")
                        arr = np.array(im)
                        print(f"  Step {step}: saved {out_path} (mean_lum={arr.mean():.1f}, non_zero={(arr > 0).mean()*100:.1f}%)")

                t.cancel()
        finally:
            try:
                urllib.request.urlopen(f'http://localhost:9222/json/close/{tab_id}')
            except: pass

asyncio.run(capture_all_kits())
