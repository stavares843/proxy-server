# proxy-server

### Requirements

- Install Python
- Install aiohttp

### Basic Authentication
- ✅ The script includes a `VALID_CREDENTIALS` setup and ensures authentication using the `Proxy-Authorization` header. This is verified through the `verify_auth` function in the `proxy_handler`.

### Track Bandwidth Usage and Most Visited Sites
- ✅ Tracks total bandwidth usage with `data_store["bandwidth_usage"]`.
- ✅ Records site visit counts in `data_store["site_visits"]`.

### Real-time Metrics Endpoint (`GET /metrics`)
- ✅ The `/metrics` endpoint, handled by the `metrics_handler` function, reports:
  - Total bandwidth usage.
  - A list of the most visited sites in JSON format.

### Final Summary on Server Shutdown
- ✅ When the server is stopped gracefully, the `on_shutdown` function prints a summary of:
  - Total bandwidth used.
  - Most visited sites.
 
<img width="272" alt="Captura de ecrã 2025-01-15, às 22 24 32" src="https://github.com/user-attachments/assets/0c48daa1-db5f-4543-99b5-312ca5a4838c" />


### Handle HTTP/HTTPS Traffic
- ✅ The script forwards HTTP/HTTPS requests using `ClientSession` in the `proxy_handler` function.

### Usage Pattern
- ✅ The proxy supports this usage pattern:
  
  ```bash
  curl -x http://proxy_server:proxy_port --proxy-user username:password -L <http://url>
  ```

### Metrics Format
- ✅ The `/metrics` endpoint returns data in the following JSON format:
  
  ```json
  {
    "bandwidth_usage": "125MB",
    "top_sites": [
      {"url": "example.com", "visits": 10},
      {"url": "google.com", "visits": 5}
    ]
  }
  ```

 ### For testing

   Run all curl commands in sequence

```

curl -x http://localhost:8080/proxy --proxy-user username:password -H "Target-URL: http://www.google.com" -L http://www.google.com && \
curl -x http://localhost:8080/proxy --proxy-user username:password -H "Target-URL: http://www.linkedin.com" -L http://www.linkedin.com && \
curl -x http://localhost:8080/proxy --proxy-user username:password -H "Target-URL: http://www.microsoft.com" -L http://www.microsoft.com && \
curl -x http://localhost:8080/proxy --proxy-user username:password -H "Target-URL: http://www.amazon.com" -L http://www.amazon.com && \
curl -x http://localhost:8080/proxy --proxy-user username:password -H "Target-URL: http://www.facebook.com" -L http://www.facebook.com

```



https://github.com/user-attachments/assets/f3ea291a-6ff1-4594-a184-0298ad793fa8


