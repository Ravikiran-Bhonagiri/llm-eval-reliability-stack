# Production Deployment - Leaving Localhost

## 🛳️ Shipping the Observatory

Running `phoenix.launch_app()` in a notebook is great for dev.
But for production (staging/prod clusters), you need a standalone **Phoenix Server**.

Detailed below is the architecture for a robust deployment.

---

## 🏗️ Architecture

You decouple the **Application** (traces generator) from the **Phoenix Server** (traces collector).

```text
    [Production App 1] --(HTTP/OTEL)--> ┐
                                        │
    [Production App 2] --(HTTP/OTEL)--> ├--> [Load Balancer] --> [Phoenix Server]
                                        │                             │
    [Worker / Job]     --(HTTP/OTEL)--> ┘                             ▼
                                                                 [Postgres DB]
```

---

## 🐳 Docker Deployment

The official image is `arize/phoenix`.

### `docker-compose.yml` (Recommended)

This sets up Phoenix with a persistent SQLite database (good for small/medium scale).

```yaml
version: "3"
services:
  phoenix:
    image: arize/phoenix:latest
    ports:
      - "6006:6006" # UI and Collector
    volumes:
      - ./phoenix_data:/phoenix/data # Persistence
    environment:
      - PHOENIX_WORKING_DIR=/phoenix/data
      - PHOENIX_PORT=6006
      - PHOENIX_GRPC_PORT=4317 # For gRPC OTEL clients
```

**Run it**:
```bash
docker-compose up -d
```

### Scaling to PostgreSQL (High Volume)
For millions of traces, SQLite locks up. Use Postgres.

```yaml
services:
  phoenix:
    image: arize/phoenix:latest
    environment:
      - PHOENIX_SQL_DATABASE_URL=postgresql://user:pass@db:5432/phoenix
  db:
    image: postgres:15
    # ... standard postgres config ...
```

---

## 🔒 Security Considerations

Phoenix is an internal tool. **Do not expose it to the public internet.**
The UI allows viewing sensitive prompt data (PII).

1.  **Network Isolation**: Put Phoenix inside your VPC (Virtual Private Cloud).
2.  **Auth**: Phoenix (OSS version) does **not** have built-in login capability.
    *   *Solution*: Put it behind an authentication proxy (like **OAuth2 Proxy** or **Cloudflare Access**) if exposing it to developers remotely.
3.  **PII Masking**: Mask sensitive data *before* it leaves your app.
    ```python
    # In your custom instrumentor
    if "credit_card" in input:
        span.set_attribute("input.value", "[REDACTED]")
    ```

---

## ⚙️ Configuration Tuning

### Sampling Rate
By default, you might trace 100% of requests.
If volume is huge (1000 req/sec), use **Probability Sampling** in your OTEL SDK.

```python
# In your App
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Sample 10%
sampler = TraceIdRatioBased(0.1)
tracer_provider = TracerProvider(sampler=sampler)
```

**Batching**
Use `BatchSpanProcessor` instead of `SimpleSpanProcessor`. It aggregates spans and sends them every 5 seconds, reducing network overhead.

---

## 🚦 Summary

1.  **Use Docker**: Don't run `python -m phoenix.server.main` in production.
2.  **Persist Data**: Map a volume or connect to Postgres.
3.  **Secure Access**: Put it behind a VPN or Auth Proxy.

Next, we bring it all together in the **Final Capstone Project**.

- **[Next: Real-World Example](./12-real-world-example.md)**

---

*Steady as she goes.* ⚓
