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
                "params": {"width": 1440, "height": 900, "deviceScaleFactor": 2, "mobile": False}
            }))
            await ws.receive_str()

            # Navigate to WineClassifier model page
            print("Navigating to Model page...")
            await ws.send_str(json.dumps({
                "id": 3,
                "method": "Page.navigate",
                "params": {"url": "http://127.0.0.1:5001/#/models/WineClassifier"}
            }))
            await ws.receive_str()
            await asyncio.sleep(4)

            # Close assistant sidebar if present
            js_close_assistant = """
            (() => {
                // Click close button on assistant if present
                const closeBtn = document.querySelector('button[aria-label="Close"], button[aria-label="Close sidebar"]');
                if (closeBtn) {
                    closeBtn.click();
                    return 'Closed assistant';
                }
                // Try finding any button with SVG close in the assistant header
                const allButtons = Array.from(document.querySelectorAll('button'));
                for (let b of allButtons) {
                    if (b.innerText === '✕' || b.innerHTML.includes('icon-cross') || b.innerHTML.includes('close')) {
                        b.click();
                        return 'Clicked close candidate';
                    }
                }
                return 'No close button found';
            })()
            """
            await ws.send_str(json.dumps({
                "id": 4,
                "method": "Runtime.evaluate",
                "params": {"expression": js_close_assistant}
            }))
            eval_res = await ws.receive_str()
            print("Close assistant result:", eval_res)
            await asyncio.sleep(2)

            # Screenshot
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
                    with open("/Users/hf/.gemini/antigravity-ide/scratch/wine-mlops-pipeline/reports/assets/real_mlflow_model.png", "wb") as f:
                        f.write(img_data)
                    print("Saved real_mlflow_model.png, size:", len(img_data))
                    break

        async with session.get(f"http://127.0.0.1:9222/json/close/{target_id}"):
            pass

asyncio.run(main())
