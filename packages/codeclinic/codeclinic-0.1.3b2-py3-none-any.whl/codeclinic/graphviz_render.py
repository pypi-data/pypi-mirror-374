from __future__ import annotations
from graphviz import Digraph
from graphviz.backend import ExecutableNotFound
from typing import Dict, Iterable, Tuple, Set
from .types import Modules, GraphEdges, ChildEdges
from .node_types import NodeInfo, NodeType


def _color_for_ratio(r: float) -> str:
    # simple traffic light
    if r <= 0.05:
        return "#4CAF50"  # green
    if r <= 0.30:
        return "#FFC107"  # amber
    return "#F44336"      # red


def _get_short_name(module_name: str) -> str:
    """Get a shortened display name for a module - only last part."""
    if not module_name:
        return "root"
    
    parts = module_name.split('.')
    
    # Always show only the last part
    return parts[-1]


def render_graph(modules: Modules, edges: GraphEdges, child_edges: ChildEdges, output_base: str, fmt: str = "svg") -> Tuple[str, str]:
    dot = Digraph(
        "codeclinic",
        graph_attr={"rankdir": "TB", "splines": "spline"},
        node_attr={"shape": "box", "style": "rounded,filled", "fontname": "Helvetica"},
        edge_attr={"arrowhead": "vee"},
    )

    for name, st in modules.items():
        ratio = st.stub_ratio
        pct = int(round(ratio * 100))
        # Use short name for display (last part of module path)
        display_name = _get_short_name(name)
        label = f"{display_name}\nstub {st.stubs}/{max(1, st.functions_public)} ({pct}%)"
        dot.node(name, label=label, fillcolor=_color_for_ratio(ratio))

    # Determine which edges have both import and child relationships
    both_relationships = set()
    import_only = set()
    child_only = set()
    
    # Find overlapping relationships
    for src, dst in edges:
        if (src, dst) in child_edges:
            both_relationships.add((src, dst))
        else:
            import_only.add((src, dst))
    
    for parent, child in child_edges:
        if (parent, child) not in edges:
            child_only.add((parent, child))
    
    # Add edges with appropriate styling
    # Both import and child: solid black line
    for src, dst in sorted(both_relationships):
        dot.edge(src, dst, color="black", style="solid")
    
    # Import only: dashed black line  
    for src, dst in sorted(import_only):
        dot.edge(src, dst, color="black", style="dashed")
    
    # Child only: dashed black line
    for parent, child in sorted(child_only):
        dot.edge(parent, child, color="black", style="dashed")

    dot_path = f"{output_base}.dot"
    svg_path = f"{output_base}.{fmt}"
    dot.save(dot_path)

    try:
        dot.render(output_base, format=fmt, cleanup=True)
    except ExecutableNotFound:
        # Only DOT written; caller should inform user
        svg_path = ""
    return dot_path, svg_path


def render_violations_graph(
    nodes: Dict[str, NodeInfo], 
    legal_edges: Set[Tuple[str, str]], 
    violation_edges: Set[Tuple[str, str]], 
    output_base: str, 
    fmt: str = "svg"
) -> Tuple[str, str]:
    """
    渲染违规检测图，用红色表示违规边，绿色表示合法边
    """
    dot = Digraph(
        "violations",
        graph_attr={"rankdir": "TB", "splines": "spline", "label": "Import Violations Graph", "labelloc": "t"},
        node_attr={"shape": "box", "style": "rounded,filled", "fontname": "Helvetica"},
        edge_attr={"arrowhead": "vee"},
    )

    # 添加节点，根据节点类型使用不同样式
    for name, node in nodes.items():
        display_name = _get_short_name(name)
        
        # 根据节点类型设置样式
        if node.node_type == NodeType.PACKAGE:
            node_color = "#E3F2FD"  # 浅蓝色
            shape = "box"
            style = "bold,filled"
        else:  # MODULE
            node_color = "#F3E5F5"  # 浅紫色
            shape = "box"
            style = "rounded,filled"
        
        label = f"{display_name}\n{node.node_type.value}"
        dot.node(name, label=label, fillcolor=node_color, shape=shape, style=style)

    # 添加合法边（绿色）
    for src, dst in sorted(legal_edges):
        if src in nodes and dst in nodes:
            dot.edge(src, dst, color="#4CAF50", style="solid", penwidth="2")

    # 添加违规边（红色）
    for src, dst in sorted(violation_edges):
        if src in nodes and dst in nodes:
            dot.edge(src, dst, color="#F44336", style="solid", penwidth="3")

    dot_path = f"{output_base}.dot"
    svg_path = f"{output_base}.{fmt}"
    dot.save(dot_path)

    try:
        dot.render(output_base, format=fmt, cleanup=True)
    except ExecutableNotFound:
        svg_path = ""
    
    return dot_path, svg_path


def render_stub_heatmap(
    nodes: Dict[str, NodeInfo], 
    edges: GraphEdges, 
    child_edges: ChildEdges, 
    output_base: str, 
    fmt: str = "svg"
) -> Tuple[str, str]:
    """
    渲染Stub热力图，节点颜色从白色（0% stub）到红色（100% stub）渐变
    """
    dot = Digraph(
        "stub_heatmap",
        graph_attr={"rankdir": "TB", "splines": "spline", "label": "Implementation Completeness Heatmap\\nProgress: 🟩 Implemented  ⬜ Stub", "labelloc": "t"},
        node_attr={"shape": "box", "style": "rounded,filled", "fontname": "Helvetica"},
        edge_attr={"arrowhead": "vee", "color": "#999999"},
    )

    # 添加节点，使用stub比例决定颜色
    for name, node in nodes.items():
        display_name = _get_short_name(name)
        ratio = node.stub_ratio
        pct = int(round(ratio * 100))
        
        # 使用统一的白色背景，不需要颜色渐变
        color = "#FFFFFF"
        
        # 根据节点类型调整显示
        if node.node_type == NodeType.PACKAGE:
            shape = "box"
            style = "bold,filled"
            type_indicator = "📦"  # package emoji
        else:  # MODULE
            shape = "box"
            style = "rounded,filled"
            type_indicator = "📄"  # file emoji
        
        # 创建进度条使用HTML表格渐变
        progress_bar = _create_html_progress_bar(ratio)
        
        # 计算实现比例（非stub）
        implemented = node.functions_public - node.stubs
        implemented_pct = int(round((1.0 - ratio) * 100))
        
        # 创建HTML标签包含进度条
        label = f'''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
            <TR><TD>{type_indicator} {display_name}</TD></TR>
            <TR><TD>{implemented}/{node.functions_public} ({implemented_pct}%)</TD></TR>
            <TR><TD>{progress_bar}</TD></TR>
        </TABLE>
        >'''
        
        dot.node(name, label=label, fillcolor=color, shape=shape, style=style)

    # 添加边（较淡的颜色，不干扰热力图）
    for src, dst in sorted(edges):
        if src in nodes and dst in nodes:
            dot.edge(src, dst, color="#CCCCCC", style="solid", penwidth="1")
    
    # 添加包含关系边（虚线）
    for parent, child in sorted(child_edges):
        if parent in nodes and child in nodes and (parent, child) not in edges:
            dot.edge(parent, child, color="#DDDDDD", style="dashed", penwidth="1")

    dot_path = f"{output_base}.dot"
    svg_path = f"{output_base}.{fmt}"
    dot.save(dot_path)

    try:
        dot.render(output_base, format=fmt, cleanup=True)
    except ExecutableNotFound:
        svg_path = ""
    
    return dot_path, svg_path


def _create_html_progress_bar(ratio: float, width: int = 120) -> str:
    """
    创建HTML表格形式的进度条，简洁显示
    
    Args:
        ratio: stub比例 (0.0 到 1.0)
        width: 进度条像素宽度
        
    Returns:
        str: HTML表格进度条
    """
    # 计算实现比例（1 - stub_ratio）
    completion_ratio = 1.0 - ratio
    completion_pct = int(round(completion_ratio * 100))
    
    # 计算进度条填充宽度
    filled_width = int(width * completion_ratio)
    empty_width = width - filled_width
    
    if completion_ratio >= 1.0:
        # 100% 完成 - 全绿色，只在第一个节点显示百分比
        progress_bar = f'''<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="ROUNDED">
            <TR>
                <TD WIDTH="{width}" HEIGHT="14" BGCOLOR="green"></TD>
            </TR>
        </TABLE>'''
    else:
        # 部分完成 - 绿色+灰色分段，只在第一个遇到的部分完成节点显示百分比
        if filled_width > 0 and empty_width > 0:
            progress_bar = f'''<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="ROUNDED">
                <TR>
                    <TD WIDTH="{filled_width}" HEIGHT="14" BGCOLOR="green"></TD>
                    <TD WIDTH="{empty_width}" HEIGHT="14" BGCOLOR="lightgray"></TD>
                </TR>
            </TABLE>'''
        elif filled_width <= 0:
            # 几乎没有完成
            progress_bar = f'''<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="ROUNDED">
                <TR>
                    <TD WIDTH="{width}" HEIGHT="14" BGCOLOR="lightgray"></TD>
                </TR>
            </TABLE>'''
        else:
            # 几乎全部完成
            progress_bar = f'''<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="ROUNDED">
                <TR>
                    <TD WIDTH="{width}" HEIGHT="14" BGCOLOR="green"></TD>
                </TR>
            </TABLE>'''
    
    return progress_bar


def _create_progress_bar(ratio: float, width: int = 10) -> str:
    """
    创建统一的进度条，用简洁的符号体现完成度
    
    Args:
        ratio: stub比例 (0.0 到 1.0)
        width: 进度条宽度
        
    Returns:
        str: 进度条字符串
    """
    # 计算实现比例（1 - stub_ratio）
    completion_ratio = 1.0 - ratio
    completion_pct = int(round(completion_ratio * 100))
    
    # 计算进度条填充长度
    filled_length = int(width * completion_ratio)
    empty_length = width - filled_length
    
    # 尝试不同的进度条样式
    if completion_ratio >= 1.0:
        # 100% 完成 - 全绿色实心条
        bar = "█" * width
        bar_display = f"🟢[{bar}] {completion_pct}%"
    else:
        # 部分完成 - 实心部分 + 空心部分
        filled = "█" * filled_length if filled_length > 0 else ""
        empty = "░" * empty_length if empty_length > 0 else ""
        bar_display = f"🟡[{filled}{empty}] {completion_pct}%"
    
    return bar_display


def _stub_ratio_to_color(ratio: float) -> str:
    """
    将stub比例转换为颜色，从白色（0%）到红色（100%）的渐变
    
    Args:
        ratio: stub比例 (0.0 到 1.0)
        
    Returns:
        str: 十六进制颜色值
    """
    # 确保ratio在0-1范围内
    ratio = max(0.0, min(1.0, ratio))
    
    # 从白色 RGB(255,255,255) 到红色 RGB(255,0,0)
    # 保持红色通道为255，绿色和蓝色通道根据ratio递减
    red = 255
    green = int(255 * (1 - ratio))
    blue = int(255 * (1 - ratio))
    
    # 转换为十六进制
    return f"#{red:02x}{green:02x}{blue:02x}"
