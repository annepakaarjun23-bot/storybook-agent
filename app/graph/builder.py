from langgraph.graph import END, START, StateGraph

from app.graph import nodes
from app.graph.state import BookState

NODE_ORDER = [
    "story_planner",
    "character_designer",
    "scene_planner",
    "quality_gate",
    "page_composer",
    "pdf_assembler",
]


def build_graph():
    graph = StateGraph(BookState)
    graph.add_node("story_planner", nodes.story_planner)
    graph.add_node("character_designer", nodes.character_designer)
    graph.add_node("scene_planner", nodes.scene_planner)
    graph.add_node("quality_gate", nodes.quality_gate)
    graph.add_node("page_composer", nodes.page_composer)
    graph.add_node("pdf_assembler", nodes.pdf_assembler)

    graph.add_edge(START, "story_planner")
    graph.add_edge("story_planner", "character_designer")
    graph.add_edge("character_designer", "scene_planner")
    graph.add_edge("scene_planner", "quality_gate")
    graph.add_conditional_edges(
        "quality_gate",
        nodes.route_after_gate,
        {"scene_planner": "scene_planner", "page_composer": "page_composer"},
    )
    graph.add_edge("page_composer", "pdf_assembler")
    graph.add_edge("pdf_assembler", END)
    return graph.compile()
