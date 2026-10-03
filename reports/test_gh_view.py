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

            print("Navigating to GitHub Actions run...")
            await ws.send_str(json.dumps({
                "id": 3,
                "method": "Page.navigate",
                "params": {"url": "https://github.com/msaleem15/wine-mlops-pipeline/actions/runs/36968754996"}
            }))
            await ws.receive_str()
            # GitHub page takes ~3-4 seconds to load
            await asyncio.sleep(4)

            # Screenshot
            await ws.send_str(json.dumps({
                "id": 4,
                "method": "Page.captureScreenshot",
                "params": {"format": "png"}
            }))

            while True:
                msg = await ws.receive_str()
                data = json.loads(msg)
                if data.get("id") == 4:
                    img_data = base64.b64decode(data["result"]["data"])
                    with open("/Users/hf/.gemini/antigravity-ide/scratch/wine-mlops-pipeline/reports/assets/real_github_action.png", "wb") as f:
                        f.write(img_data)
                    print("Saved real_github_action.png, size:", len(img_data))
                    break

        async with session.get(f"http://127.0.0.1:9222/json/close/{target_id}"):
            pass

asyncio.run(main())
