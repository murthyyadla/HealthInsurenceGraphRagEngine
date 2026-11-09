
import sys
import os

# Dynamically append the project root directory to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now your original import will work perfectly
from src.pipeline import myhealthinsure_pipeline

def export_pipeline_visualization():
    print("🕸️ Compiling myHealthInsure LangGraph State Machine Architecture...")
    mermaid_string = myhealthinsure_pipeline.get_graph().draw_mermaid()
    with open("myhealthinsure_architecture.txt", "w") as f:
        f.write(mermaid_string)
    print("💾 Saved raw Mermaid code structural asset to 'myhealthinsure_architecture.txt'.")

if __name__ == "__main__":
    export_pipeline_visualization()
