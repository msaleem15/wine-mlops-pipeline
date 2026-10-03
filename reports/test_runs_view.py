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

            # 1600x900 viewport
            await ws.send_str(json.dumps({
                "id": 2,
                "method": "Emulation.setDeviceMetricsOverride",
                "params": {"width": 1600, "height": 900, "deviceScaleFactor": 2, "mobile": False}
            }))
            await ws.receive_str()

            print("Navigating to MLflow runs...")
            await ws.send_str(json.dumps({
                "id": 3,
                "method": "Page.navigate",
                "params": {"url": "http://127.0.0.1:5001/#/experiments/1"}
            }))
            await ws.receive_str()
            await asyncio.sleep(4)

            # Click 'Training runs' tab and close assistant
            js_action = """
            (() => {
                // 1. Close assistant
                const allButtons = Array.from(document.querySelectorAll('button'));
                for (let b of allButtons) {
                    if (b.getAttribute('aria-label') === 'Close' || b.innerText === '✕') {
                        b.click();
                    }
                }
                // Also close any 'Got it' modal if present
                const gotIt = allButtons.find(b => b.innerText && b.innerText.trim() === 'Got it');
                if (gotIt) gotIt.click();

                // 2. Click Training runs tab
                const tabs = Array.from(document.querySelectorAll('a, button, div[role="tab"], span'));
                const tr = tabs.find(el => el.textContent && el.textContent.trim() === 'Training runs');
                if (tr) tr.click();

                return 'Done initial clicks';
            })()
            """
            await ws.send_str(json.dumps({
                "id": 4,
                "method": "Runtime.evaluate",
                "params": {"expression": js_action}
            }))
            await ws.receive_str()
            await asyncio.sleep(3)

            # Close assistant again if still present, and check columns
            js_clean = """
            (() => {
                const allButtons = Array.from(document.querySelectorAll('button'));
                for (let b of allButtons) {
                    if (b.getAttribute('aria-label') === 'Close' || b.getAttribute('aria-label') === 'Close sidebar') {
                        b.click();
                    }
                }
                // Try scrolling table right if it exists
                const tableContainer = document.querySelector('.ag-body-viewport, [role="grid"], div[class*="table"]');
                return 'Cleaned';
            })()
            """
            await ws.send_str(json.dumps({
                "id": 5,
                "method": "Runtime.evaluate",
                "params": {"expression": js_clean}
            }))
            await ws.receive_str()
            await asyncio.sleep(2)

            # Screenshot of Runs table
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
                    with open("/Users/hf/.gemini/antigravity-ide/scratch/wine-mlops-pipeline/reports/assets/real_mlflow_runs_table.png", "wb") as f:
                        f.write(img_data)
                    print("Saved real_mlflow_runs_table.png, size:", len(img_data))
                    break

            # Now let's try switching to Chart View!
            js_click_chart = """
            (() => {
                // Find chart view toggle icon
                const viewToggles = Array.from(document.querySelectorAll('div[role="radio"], button, svg'));
                // Look for chart icon
                for (let el of document.querySelectorAll('button, div[role="radio"]')) {
                    if (el.innerHTML.includes('line-chart') || el.innerHTML.includes('chart') || el.getAttribute('aria-label') === 'Chart view') {
                        el.click();
                        return 'Clicked chart toggle';
                    }
                }
                // Or look for svg with line chart
                return 'Chart toggle search finished';
            })()
            """
            await ws.send_str(json.dumps({
                "id": 7,
                "method": "Runtime.evaluate",
                "params": {"expression": js_click_chart}
            }))
            await ws.receive_str()
            await asyncio.sleep(3)

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
                    with open("/Users/hf/.gemini/antigravity-ide/scratch/wine-mlops-pipeline/reports/assets/real_mlflow_chart_view.png", "wb") as f:
                        f.write(img_data)
                    print("Saved real_mlflow_chart_view.png, size:", len(img_data))
                    break

        async with session.get(f"http://127.0.0.1:9222/json/close/{target_id}"):
            pass

asyncio.run(main())
