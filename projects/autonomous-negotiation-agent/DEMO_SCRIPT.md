# Demo & Artifact Generation Script

## 🎥 Recording the Demo Video (The "Money" Shot)

**Objective**: Record a 60-second clip showing the "Red Trace -> Prompt Fix -> Green Trace" workflow.

**Script:**
1.  **Scene 1: The Bug (0:00 - 0:20)**
    *   Run `python main.py`.
    *   Show the console output.
    *   Switch to Phoenix UI (`localhost:6006`).
    *   Click the **Failed Trace** (Red). Use zoom to show `ValueError: '$48'`.

2.  **Scene 2: The Diagnosis (0:20 - 0:40)**
    *   Click **"Open in Playground"** button in Phoenix.
    *   Edit the System Prompt in the left panel.
    *   Add text: *"OUTPUT RAW NUMBERS ONLY"*.
    *   Click **Run**. Show the tool call successfully outputting `48.0`.

3.  **Scene 3: The Fix (0:40 - 1:00)**
    *   Copy the fixed prompt back to `src/negotiation_graph.py`.
    *   Re-run `python main.py`.
    *   Show the **Green Trace** in Phoenix.
    *   **End**.

---

## 📐 Creating the Architecture Diagram

**Objective**: Visualize the LangGraph nodes.

**Instructions:**
1.  Use **Mermaid.js** or **Excalidraw**.
2.  Draw 3 Nodes: `Buyer`, `Supplier`, `Supervisor`.
3.  Draw Arrows:
    *   Buyer -> Supervisor
    *   Supplier -> Supervisor
    *   Supervisor -> Buyer (Loop)
    *   Supervisor -> Supplier (Loop)
    *   Supervisor -> End
4.  Save as `architecture_diagram.png` in this folder.
