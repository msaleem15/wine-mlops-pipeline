import asyncio
import json
import base64
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.put("http://127.0.0.1:9222/json/new") as resp:
            page_info = await resp.json()
            ws_url = page_info["webSocketDebuggerUrl"]
            target_id = page_info["id"]

        async with session.ws_connect(ws_url) as ws:
            await ws.send_str(json.dumps({"id": 1, "method": "Page.enable"}))
            await ws.receive_str()

            await ws.send_str(json.dumps({
                "id": 2,
                "method": "Emulation.setDeviceMetricsOverride",
                "params": {"width": 1600, "height": 950, "deviceScaleFactor": 2, "mobile": False}
            }))
            await ws.receive_str()

            await ws.send_str(json.dumps({
                "id": 3,
                "method": "Page.navigate",
                "params": {"url": "http://127.0.0.1:5001/#/experiments/1"}
            }))
            await ws.receive_str()
            await asyncio.sleep(4)

            # Close assistant and click training runs
            js = """
            (() => {
                // close assistant
                const allButtons = Array.from(document.querySelectorAll('button'));
                for (let b of allButtons) {
                    if (b.getAttribute('aria-label') === 'Close') b.click();
                    if (b.innerText && b.innerText.trim() === 'Got it') b.click();
                }
                const tabs = Array.from(document.querySelectorAll('a, button, div[role="tab"], span'));
                const tr = tabs.find(el => el.textContent && el.textContent.trim() === 'Training runs');
                if (tr) tr.click();
                return 'Init clicked';
            })()
            """
            await ws.send_str(json.dumps({"id": 4, "method": "Runtime.evaluate", "params": {"expression": js}}))
            await ws.receive_str()
            await asyncio.sleep(3)

            # Collapse sidebar and click 'Show more columns'
            js2 = """
            (() => {
                // Find collapse sidebar button (near mlflow 3.16.1)
                const allButtons = Array.from(document.querySelectorAll('button'));
                for (let b of allButtons) {
                    if (b.getAttribute('aria-label') && b.getAttribute('aria-label').toLowerCase().includes('collapse')) {
                        b.click();
                    }
                }

                // Click 'Show more columns'
                const elements = Array.from(document.querySelectorAll('button, div, span'));
                const showMore = elements.find(el => el.innerText && el.innerText.includes('Show more columns'));
                if (showMore) {
                    showMore.click();
                    return 'Clicked show more columns';
                }
                return 'Show more not found';
            })()
            """
            await ws.send_str(json.dumps({"id": 5, "method": "Runtime.evaluate", "params": {"expression": js2}}))
            eval_res = await ws.receive_str()
            print("Show more result:", eval_res)
            await asyncio.sleep(2)

            # Screenshot
            await ws.send_str(json.dumps({
                "id": 6,
                "method": "Page.captureScreenshot",
                "params": {"format": "png"}
            }))

            while True:
                msg = await ws.receive_str()
                data = json.loads(msg)
                if data.get("id") == 6:
                    img_data = base64.b64decode(data["result"]["data"])
                    with open("/Users/hf/.gemini/antigravity-ide/scratch/wine-mlops-pipeline/reports/assets/real_mlflow_runs_expanded.png", "wb") as f:
                        f.write(img_data)
                    print("Saved real_mlflow_runs_expanded.png, size:", len(img_data))
                    break

        async with session.get(f"http://127.0.0.1:9222/json/close/{target_id}"):
            pass

asyncio.run(main())
