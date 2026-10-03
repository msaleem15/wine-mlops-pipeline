import asyncio
import json
import base64
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        # Get target page or create new one
        async with session.put("http://127.0.0.1:9222/json/new") as resp:
            page_info = await resp.json()
            ws_url = page_info["webSocketDebuggerUrl"]
            target_id = page_info["id"]

        print(f"Connecting to ws: {ws_url}")
        async with session.ws_connect(ws_url) as ws:
            # Enable Page
            await ws.send_str(json.dumps({"id": 1, "method": "Page.enable"}))
            await ws.receive_str()

            # Set viewport
            await ws.send_str(json.dumps({
                "id": 2,
                "method": "Emulation.setDeviceMetricsOverride",
                "params": {"width": 1440, "height": 900, "deviceScaleFactor": 2, "mobile": False}
            }))
            await ws.receive_str()

            # Navigate to MLflow experiments
            print("Navigating to MLflow...")
            await ws.send_str(json.dumps({
                "id": 3,
                "method": "Page.navigate",
                "params": {"url": "http://127.0.0.1:5001/#/experiments/1"}
            }))
            await ws.receive_str()

            # Wait 4 seconds for react app to load
            await asyncio.sleep(4)

            # Click on 'Training runs' or 'Model training' or find tab
            # Let's inspect page title or evaluate JS
            js_script = """
            (() => {
                // Find and click the 'Training runs' tab
                const tabs = Array.from(document.querySelectorAll('a, button, div[role="tab"], span'));
                const tr = tabs.find(el => el.textContent && el.textContent.trim() === 'Training runs');
                if (tr) {
                    tr.click();
                    return 'Clicked Training runs';
                }
                const mt = tabs.find(el => el.textContent && el.textContent.trim() === 'Model training');
                if (mt) {
                    mt.click();
                    return 'Clicked Model training';
                }
                return 'No tab found';
            })()
            """
            await ws.send_str(json.dumps({
                "id": 4,
                "method": "Runtime.evaluate",
                "params": {"expression": js_script}
            }))
            eval_res = await ws.receive_str()
            print("Tab click result:", eval_res)

            # Wait 3 seconds after click
            await asyncio.sleep(3)

            # Capture screenshot
            await ws.send_str(json.dumps({
                "id": 5,
                "method": "Page.captureScreenshot",
                "params": {"format": "png"}
            }))
            
            while True:
                msg = await ws.receive_str()
                data = json.loads(msg)
                if data.get("id") == 5:
                    img_data = base64.b64decode(data["result"]["data"])
                    with open("/Users/hf/.gemini/antigravity-ide/scratch/wine-mlops-pipeline/reports/assets/real_mlflow_runs.png", "wb") as f:
                        f.write(img_data)
                    print("Saved real_mlflow_runs.png, size:", len(img_data))
                    break

        # Close target
        async with session.get(f"http://127.0.0.1:9222/json/close/{target_id}"):
            pass

asyncio.run(main())
