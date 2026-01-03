# Infrastructure & Installation - The Data Platform

## 🏗️ Designing the Observability Layer

In a production LLM system, the **Observability Layer** must be decoupled from the **Application Layer**.
If your App crashes, you don't want your Logs to die with it.

This guide covers setting up Arize Phoenix as a persistent, standalone service.

---

## 🧩 The Architecture

We are building this:

```
    [ User Traffic ]
           │
           ▼
    [ Your LLM App ] <--- (Async SDK) ---> [ Auto-Instrumentor ]
                                                  │
                                          (OTLP over HTTP)
                                                  │
                                                  ▼
                                         [ Phoenix Server ]
                                                  │
                                          (Write / Read)
                                                  │
                                                  ▼
                                         [ Storage Layer ]
                                       (SQLite or Postgres)
```

---

## 🖥️ Local Development Setup (Level 1)

For rapid iteration on your laptop, we use `pip`.

### 1. Installation
```bash
pip install arize-phoenix openinference-instrumentation-openai opentelemetry-sdk
```

### 2. The Persistence Problem
By default, `phoenix.launch_app()` runs in-memory. **If you restart the script, you lose all traces.**
For deep research, you *need* history.

### 3. Solving Persistence (Local)
We must bind Phoenix to a local directory or database file.

```python
# infrastructure.py
import phoenix as px
import os

# Define a permanent home for data
PHOENIX_DIR = os.path.join(os.getcwd(), "phoenix_data")
os.makedirs(PHOENIX_DIR, exist_ok=True)

# Launch with persistence (SQLite backend)
os.environ["PHOENIX_WORKING_DIR"] = PHOENIX_DIR

session = px.launch_app()
print(f"Phoenix UI running at: {session.url}")
print(f"Data stored in: {PHOENIX_DIR}")

# Keep alive
input("Press Enter to stop server...")
```

---

## 🐋 Production Container Setup (Level 2)

For staging/prod, we never use `pip run`. We use **Docker**.
This ensures the Observability Server is isolated from the App container.

### `docker-compose.yml`

Create this file in your root:

```yaml
version: '3.8'

services:
  # The Observability Server
  phoenix:
    image: arize/phoenix:latest
    container_name: phoenix_server
    ports:
      - "6006:6006"   # API and UI
      - "4317:4317"   # gRPC Endpoint (Fast)
    volumes:
      - ./phoenix_storage:/phoenix/data
    environment:
      - PHOENIX_PORT=6006
      - PHOENIX_WORKING_DIR=/phoenix/data
    restart: always

  # Your LLM Application (Example)
  llm_app:
    build: .
    environment:
      # Point to the Phoenix Container!
      - PHOENIX_COLLECTOR_ENDPOINT=http://phoenix_server:6006/v1/traces
    depends_on:
      - phoenix
```

**Why this is better**:
1.  **Network Isolation**: The app talks to Phoenix over the internal Docker network `phoenix_server`.
2.  **Volume Mapping**: Even if you destroy the containers, `./phoenix_storage` keeps your traces.
3.  **Performance**: The App only needs to send data; it doesn't spend CPU rendering the UI.

---

## 🔌 Connection Verification (The Handshake)

Before building massive apps, verify the pipe works.

### `verify_connection.py`

```python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# 1. Config
COLLECTOR_ENDPOINT = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
resource = Resource(attributes={"service.name": "connection-verifier"})

# 2. Setup OTEL Pipeline
provider = TracerProvider(resource=resource)
# SimpleSpanProcessor sends IMMEDIATELY (good for test). 
# BatchSpanProcessor is better for prod.
processor = SimpleSpanProcessor(OTLPSpanExporter(endpoint=COLLECTOR_ENDPOINT))
provider.add_span_processor(processor)

# 3. Create Tracer
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# 4. Generate Test Span
print(f"📡 Sending handshake to {COLLECTOR_ENDPOINT}...")
with tracer.start_as_current_span("infrastructure_handshake") as span:
    span.set_attribute("status", "operational")
    span.set_attribute("version", "1.0.0")
    print("✅ Span created.")

print("Check UI for 'infrastructure_handshake' trace.")
```

---

## 🚦 Summary

You now have a robust data platform.

*   **Local**: Use `PHOENIX_WORKING_DIR` to save data.
*   **Production**: Use Docker Compose to isolate the server.
*   **Verification**: Use `verify_connection.py` to prove the network path is open.

Now that the *platform* is ready, we need to understand the *data* we are sending to it.

- **[Next: Block 3 - Tracing Theory](./03-tracing-theory.md)**
