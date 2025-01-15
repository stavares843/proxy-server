import asyncio
from aiohttp import web, ClientSession
from collections import defaultdict
import json

# bandwidth usage and site tracking
data_store = {
    "bandwidth_usage": 0,  # in bytes
    "site_visits": defaultdict(int)  # url -> visits
}

# basic authentication
VALID_CREDENTIALS = {"username": "password"}

async def proxy_handler(request):
    """Handles proxy requests and forwards them to the target URL."""
    print("Request Path:", request.path)
    print("Request Headers:", request.headers)
    print("Target-URL Header:", request.headers.get("Target-URL"))

    # Parse and verify authentication
    auth_header = request.headers.get("Proxy-Authorization")
    if not auth_header or not verify_auth(auth_header):
        return web.Response(status=407, headers={"Proxy-Authenticate": "Basic"})

    # Parse target URL
    target_url = request.headers.get("Target-URL")
    if not target_url:
        return web.Response(status=400, text="Target-URL header is required")

    # tracks site visits
    site = target_url.split("/")[2]
    data_store["site_visits"][site] += 1

    # forward the request and track bandwidth usage
    try:
        async with ClientSession() as session:
            async with session.request(
                method=request.method,
                url=target_url,
                headers={key: value for key, value in request.headers.items() if key != "Target-URL"},
                data=await request.read()
            ) as resp:
                body = await resp.read()
                data_store["bandwidth_usage"] += len(body)

                return web.Response(status=resp.status, headers=resp.headers, body=body)
    except Exception as e:
        return web.Response(status=502, text=f"Error forwarding request: {e}")

async def metrics_handler(request):
    """Provides real-time metrics on bandwidth usage and top sites."""
    metrics = {
        "bandwidth_usage": f"{data_store['bandwidth_usage'] / (1024 * 1024):.2f}MB",
        "top_sites": sorted(
            (
                {"url": site, "visits": visits}
                for site, visits in data_store["site_visits"].items()
            ),
            key=lambda x: -x["visits"]
        )
    }

    html_content = f"""
    <html>
        <head>
            <title>Proxy Metrics</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #74ebd5, #9face6);
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 50px auto;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                h1 {{
                    background: #4facfe;
                    background: linear-gradient(to right, #00f2fe, #4facfe);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    margin: 0;
                }}
                p {{
                    font-size: 18px;
                    padding: 20px;
                    margin: 0;
                    border-bottom: 1px solid #eee;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 15px;
                    text-align: left;
                }}
                th {{
                    background-color: #f4f4f4;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Proxy Metrics</h1>
                <p><strong>Bandwidth Usage:</strong> {metrics["bandwidth_usage"]}</p>
                <div>
                    <table>
                        <thead>
                            <tr>
                                <th>URL</th>
                                <th>Visits</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(f"<tr><td>{site['url']}</td><td>{site['visits']}</td></tr>" for site in metrics["top_sites"])}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
    </html>
    """
    return web.Response(text=html_content, content_type="text/html")

async def on_shutdown(app):
    """Logs final summary metrics on server shutdown."""
    print("Shutting down... Final summary:")
    print(json.dumps({
        "bandwidth_usage": f"{data_store['bandwidth_usage'] / (1024 * 1024):.2f}MB",
        "top_sites": sorted(
            (
                {"url": site, "visits": visits}
                for site, visits in data_store["site_visits"].items()
            ),
            key=lambda x: -x["visits"]
        )
    }, indent=2))

# Helper: Verify Basic Auth
def verify_auth(auth_header):
    """verifies the provided basic auth credentials."""
    try:
        import base64
        auth_type, encoded = auth_header.split(" ")
        if auth_type.lower() != "basic":
            return False
        decoded = base64.b64decode(encoded).decode()
        username, password = decoded.split(":")
        return VALID_CREDENTIALS.get(username) == password
    except Exception:
        return False

# main app setup
app = web.Application()
app.router.add_route('*', '/{path:.*}', proxy_handler)  # match all paths
app.router.add_get('/metrics', metrics_handler)    # metrics route

app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    import sys
    try:
        web.run_app(app, port=8080)
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, shutting down gracefully...")
        asyncio.run(on_shutdown(app))
        sys.exit(0)
