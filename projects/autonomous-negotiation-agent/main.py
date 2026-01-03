import os
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor
from src.negotiation_graph import workflow, AgentState
from langchain_core.messages import HumanMessage

# 1. Configure OpenTelemetry
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:4317"
os.environ["PHOENIX_PROJECT_NAME"] = "supply-chain-negotiator"

# 2. Auto-Instrument
LangChainInstrumentor().instrument()

# 3. Compile
app = workflow.compile()

print("🚀 Starting Negotiation Simulation...")
initial_state = AgentState(
    messages=[HumanMessage(content="I need to buy 500 units of your X100 chip.")],
    current_offer=0.0,
    negotiation_status="open",
    turn_count=0
)

# 4. Run (Traces sent to Phoenix)
try:
    final_state = app.invoke(initial_state)
    print(f"✅ Simulation Complete. View traces at http://localhost:6006")
except Exception as e:
    print(f"❌ Simulation Failed: {e}")
