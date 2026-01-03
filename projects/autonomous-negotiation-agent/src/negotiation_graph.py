import operator
from typing import TypedDict, Annotated, List, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# --- Shared State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_offer: float
    negotiation_status: str
    turn_count: int

# --- Tool Definitions ---
@tool
def sign_contract(price: float) -> str:
    """
    Finalizes the deal. 
    CRITICAL: 'price' must be a raw number (e.g., 45.50), NOT a string like '$45'.
    """
    print(f"[BACKEND] Processing contract for ${price}...")
    return "CONTRACT_SIGNED_SUCCESS"

# --- Agents ---
llm = ChatOpenAI(model="gpt-4", temperature=0.6)

def buyer_agent(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Procurement Manager at Tesla. Budget: $50. "
                   "Current Status: {status}. Last Offer: ${offer}. "
                   "Goal: Negotiate the lowest price."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm
    
    # Simple parsing logic for demo (in production use tools/parsers)
    response = chain.invoke({
        "messages": state['messages'],
        "status": state['negotiation_status'],
        "offer": state['current_offer']
    })
    
    # Heuristic to update offer in state (simplified)
    # In real app, use structured output or tools to extract price
    return {"messages": [response], "turn_count": state['turn_count'] + 1}

def supplier_agent(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a chip supplier. Minimum Price: $45. "
                   "If the buyer offers >= $45, accept it by calling the 'sign_contract' tool. "
                   "IMPORTANT: When calling 'sign_contract', output the price as a raw number ONLY (e.g., 48.0). Do NOT include '$' symbols."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm.bind_tools([sign_contract])
    response = chain.invoke({"messages": state['messages']})
    
    return {"messages": [response]}

def route_step(state: AgentState) -> Literal["supplier", "buyer", "end"]:
    if state['turn_count'] > 10:
        return "end"
        
    last_msg = state['messages'][-1]
    
    # Check for Tool Calls
    if hasattr(last_msg, 'tool_calls') and len(last_msg.tool_calls) > 0:
        return "end" 
        
    # Turn Taking
    if isinstance(last_msg, HumanMessage):
        return "supplier"
    if "Procurement Manager" in last_msg.content:
        return "supplier"
    return "buyer"

# --- Graph Construction ---
workflow = StateGraph(AgentState)
workflow.add_node("buyer", buyer_agent)
workflow.add_node("supplier", supplier_agent)

workflow.set_entry_point("buyer") # In demo we might start with human message though

workflow.add_conditional_edges(
    "buyer",
    route_step,
    {
        "supplier": "supplier",
        "end": END
    }
)
workflow.add_conditional_edges(
    "supplier",
    route_step,
    {
        "buyer": "buyer",
        "end": END
    }
)
