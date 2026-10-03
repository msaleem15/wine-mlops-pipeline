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

            # High-res wide viewport
            await ws.send_str(json.dumps({
                "id": 2,
                "method": "Emulation.setDeviceMetricsOverride",
                "params": {"width": 1920, "height": 1080, "deviceScaleFactor": 2, "mobile": False}
            }))
            await ws.receive_str()

            await ws.send_str(json.dumps({
                "id": 3,
                "method": "Page.navigate",
                "params": {"url": "http://127.0.0.1:5001/#/experiments/1"}
            }))
            await ws.receive_str()
            await asyncio.sleep(4)

            # Close assistant, click training runs, open columns dropdown, select metrics and params, close dropdown
            js = """
            (() => {
                // 1. Close assistant
                const allButtons = Array.from(document.querySelectorAll('button'));
                for (let b of allButtons) {
                    if (b.getAttribute('aria-label') === 'Close') b.click();
                    if (b.innerText && b.innerText.trim() === 'Got it') b.click();
                }
                // 2. Training runs tab
                const tabs = Array.from(document.querySelectorAll('a, button, div[role="tab"], span'));
                const tr = tabs.find(el => el.textContent && el.textContent.trim() === 'Training runs');
                if (tr) tr.click();
            })()
            """
            await ws.send_str(json.dumps({"id": 4, "method": "Runtime.evaluate", "params": {"expression": js}}))
            await ws.receive_str()
            await asyncio.sleep(3)

            # Open Columns dropdown
            js_open_cols = """
            (() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const colBtn = buttons.find(b => b.innerText && b.innerText.includes('Columns'));
                if (colBtn) {
                    colBtn.click();
                    return 'Clicked Columns';
                }
                return 'No Columns button';
            })()
            """
            await ws.send_str(json.dumps({"id": 5, "method": "Runtime.evaluate", "params": {"expression": js_open_cols}}))
            eval_res = await ws.receive_str()
            print("Open cols:", eval_res)
            await asyncio.sleep(2)

            # Select Metrics and Parameters checkboxes
            js_select_all = """
            (() => {
                const labels = Array.from(document.querySelectorAll('label, div, span'));
                // Find Metrics (6) and Parameters (6)
                for (let el of labels) {
                    if (el.innerText && (el.innerText.trim().startsWith('Metrics') || el.innerText.trim().startsWith('Parameters'))) {
                        // Click either checkbox inside or the element itself
                        const cb = el.querySelector('input[type="checkbox"]');
                        if (cb && !cb.checked) {
                            cb.click();
                        } else {
                            el.click();
                        }
                    }
                }
                // Also explicitly check all checkboxes under metrics/params if any
                const allCheckboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
                for (let cb of allCheckboxes) {
                    if (!cb.checked) {
                        cb.click();
                    }
                }
                return 'Checked columns';
            })()
            """
            await ws.send_str(json.dumps({"id": 6, "method": "Runtime.evaluate", "params": {"expression": js_select_all}}))
            eval_res2 = await ws.receive_str()
            print("Select cols:", eval_res2)
            await asyncio.sleep(2)

            # Close dropdown by clicking header or pressing escape
            js_close_dropdown = """
            (() => {
                const header = document.querySelector('h1, h2, h3, [class*="Header"], [role="banner"]');
                if (header) header.click();
            })()
            """
            await ws.send_str(json.dumps({"id": 7, "method": "Runtime.evaluate", "params": {"expression": js_close_dropdown}}))
            await ws.receive_str()
            await asyncio.sleep(2)

            # Capture screenshot
            await ws.send_str(json.dumps({
                "id": 8,
                "method": "Page.captureScreenshot",
                "params": {"format": "png"}
            }))

            while True:
                msg = await ws.receive_str()
                data = json.loads(msg)
                if data.get("id") == 8:
                    img_data = base64.b64decode(data["result"]["data"])
                    with open("/Users/hf/.gemini/antigravity-ide/scratch/wine-mlops-pipeline/reports/assets/real_mlflow_runs_full.png", "wb") as f:
                        f.write(img_data)
                    print("Saved real_mlflow_runs_full.png, size:", len(img_data))
                    break

        async with session.get(f"http://127.0.0.1:9222/json/close/{target_id}"):
            pass

asyncio.run(main())
