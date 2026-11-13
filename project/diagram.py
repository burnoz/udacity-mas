import os
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def create_diagram(title, nodes, edges, node_labels=None, node_types=None, edge_labels=None):
    graph = nx.DiGraph()

    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    if node_labels is None:
        node_labels = {node: node for node in nodes}
    if node_types is None:
        node_types = {node: 'agent' for node in nodes}
    if edge_labels is None:
        edge_labels = {}

    plt.figure(figsize=(16, 10))
    plt.title(title, fontsize=16, fontweight='bold', pad=20)

    pos = {}
    horizontal_spacing = 1.4
    vertical_spacing = 1.0

    # Column 0: User Interface
    pos["Customer Inquiry"] = (0, 0)

    # Column 1: Orchestrator Agent
    pos["Orchestrator Agent"] = (1 * horizontal_spacing, 0)

    # Column 2: Specialized Worker Agents
    pos["Inventory Agent"] = (2 * horizontal_spacing, 1.25 * vertical_spacing)
    pos["Quoting Agent"] = (2 * horizontal_spacing, 0)
    pos["Transaction Agent"] = (2 * horizontal_spacing, -1.25 * vertical_spacing)

    # Column 3: Tools (organized by agent responsibility)
    pos["Check Inventory Tool\n(get_all_inventory /\nget_stock_level)"] = (3.25 * horizontal_spacing, 1.65 * vertical_spacing)
    pos["Supplier Delivery Tool\n(get_supplier_delivery_date)"] = (3.25 * horizontal_spacing, 0.85 * vertical_spacing)
    pos["Quote History Tool\n(search_quote_history)"] = (3.25 * horizontal_spacing, 0.30 * vertical_spacing)
    pos["Discount & Pricing Tool\n(paper_supplies + bulk tiers)"] = (3.25 * horizontal_spacing, -0.30 * vertical_spacing)
    pos["Fulfill Order Tool\n(create_transaction:\nsales & stock_orders)"] = (3.25 * horizontal_spacing, -0.90 * vertical_spacing)
    pos["Cash & Report Tool\n(get_cash_balance /\ngenerate_financial_report)"] = (3.25 * horizontal_spacing, -1.65 * vertical_spacing)

    # Column 4: Data Component
    pos["DB\n(SQLite)"] = (4.55 * horizontal_spacing, 0)

    node_colors = []
    node_shapes = []
    node_sizes = []

    for node in nodes:
        node_type = node_types.get(node, 'agent')

        if node_type == 'agent':
            node_colors.append("#6495ED")
            node_shapes.append('o')
            node_sizes.append(2800)
        elif node_type == 'tool':
            node_colors.append("#FFD700")
            node_shapes.append('s')
            node_sizes.append(2600)
        elif node_type == 'user':
            node_colors.append("#FF6347")
            node_shapes.append('d')
            node_sizes.append(2400)
        elif node_type == 'data':
            node_colors.append("#90EE90")
            node_shapes.append('h')
            node_sizes.append(2500)
        else:
            node_colors.append("#C0C0C0")
            node_shapes.append('p')
            node_sizes.append(2300)

    for i, node in enumerate(nodes):
        nx.draw_networkx_nodes(
            graph, pos,
            nodelist=[node],
            node_color=[node_colors[i]],
            node_shape=node_shapes[i],
            node_size=node_sizes[i],
            edgecolors='black',
            linewidths=1.5,
            alpha=0.9
        )

    nx.draw_networkx_edges(
        graph, pos,
        edge_color="black",
        arrowsize=22,
        width=1.8,
        alpha=0.85,
        arrowstyle='-|>',
        connectionstyle="arc3,rad=0.08"
    )

    for node, (x, y) in pos.items():
        plt.text(
            x, y, node_labels[node],
            fontsize=9.5,
            ha='center',
            va='center',
            fontweight='bold',
            bbox=dict(
                facecolor='white',
                alpha=0.85,
                edgecolor='lightgray',
                boxstyle='round,pad=0.4'
            )
        )

    if edge_labels:
        for edge, label in edge_labels.items():
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            x = (x1 + x2) / 2
            # Offset upward for forward edges, downward for return edges
            y_offset = 0.16 if x1 <= x2 else -0.18
            y = (y1 + y2) / 2 + y_offset
            plt.text(
                x, y, label,
                fontsize=8.5,
                ha='center',
                va='center',
                fontweight='bold',
                color='darkblue',
                bbox=dict(
                    facecolor='white',
                    alpha=0.9,
                    edgecolor='blue',
                    boxstyle='round,pad=0.25'
                )
            )

    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor="#6495ED", markersize=15, label='Agent'),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor="#FFD700", markersize=15, label='Tool/Resource'),
        plt.Line2D([0], [0], marker='d', color='w', markerfacecolor="#FF6347", markersize=15, label='User Interface'),
        plt.Line2D([0], [0], marker='h', color='w', markerfacecolor="#90EE90", markersize=15, label='Data Component')
    ]
    plt.legend(handles=legend_elements, loc='upper right', fontsize=11)

    plt.axis("off")
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflow_diagram.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()


def beavers_choice_solution():
    nodes = [
        # User Interface
        "Customer Inquiry",

        # Agents
        "Orchestrator Agent",
        "Inventory Agent",
        "Quoting Agent",
        "Transaction Agent",

        # Inventory Tools
        "Check Inventory Tool\n(get_all_inventory /\nget_stock_level)",
        "Supplier Delivery Tool\n(get_supplier_delivery_date)",

        # Quoting Tools
        "Quote History Tool\n(search_quote_history)",
        "Discount & Pricing Tool\n(paper_supplies + bulk tiers)",

        # Transaction / Financial Tools
        "Fulfill Order Tool\n(create_transaction:\nsales & stock_orders)",
        "Cash & Report Tool\n(get_cash_balance /\ngenerate_financial_report)",

        # Data Component
        "DB\n(SQLite)"
    ]

    edges = [
        # User <-> Orchestrator
        ("Customer Inquiry", "Orchestrator Agent"),
        ("Orchestrator Agent", "Customer Inquiry"),

        # Orchestrator <-> Worker Agents
        ("Orchestrator Agent", "Inventory Agent"),
        ("Inventory Agent", "Orchestrator Agent"),
        ("Orchestrator Agent", "Quoting Agent"),
        ("Quoting Agent", "Orchestrator Agent"),
        ("Orchestrator Agent", "Transaction Agent"),
        ("Transaction Agent", "Orchestrator Agent"),

        # Inventory Agent <-> Tools
        ("Inventory Agent", "Check Inventory Tool\n(get_all_inventory /\nget_stock_level)"),
        ("Check Inventory Tool\n(get_all_inventory /\nget_stock_level)", "Inventory Agent"),
        ("Inventory Agent", "Supplier Delivery Tool\n(get_supplier_delivery_date)"),
        ("Supplier Delivery Tool\n(get_supplier_delivery_date)", "Inventory Agent"),

        # Quoting Agent <-> Tools
        ("Quoting Agent", "Quote History Tool\n(search_quote_history)"),
        ("Quote History Tool\n(search_quote_history)", "Quoting Agent"),
        ("Quoting Agent", "Discount & Pricing Tool\n(paper_supplies + bulk tiers)"),
        ("Discount & Pricing Tool\n(paper_supplies + bulk tiers)", "Quoting Agent"),

        # Transaction Agent <-> Tools
        ("Transaction Agent", "Fulfill Order Tool\n(create_transaction:\nsales & stock_orders)"),
        ("Fulfill Order Tool\n(create_transaction:\nsales & stock_orders)", "Transaction Agent"),
        ("Transaction Agent", "Cash & Report Tool\n(get_cash_balance /\ngenerate_financial_report)"),
        ("Cash & Report Tool\n(get_cash_balance /\ngenerate_financial_report)", "Transaction Agent"),

        # Tools <-> SQLite Database
        ("Check Inventory Tool\n(get_all_inventory /\nget_stock_level)", "DB\n(SQLite)"),
        ("DB\n(SQLite)", "Check Inventory Tool\n(get_all_inventory /\nget_stock_level)"),
        ("Quote History Tool\n(search_quote_history)", "DB\n(SQLite)"),
        ("DB\n(SQLite)", "Quote History Tool\n(search_quote_history)"),
        ("Fulfill Order Tool\n(create_transaction:\nsales & stock_orders)", "DB\n(SQLite)"),
        ("Cash & Report Tool\n(get_cash_balance /\ngenerate_financial_report)", "DB\n(SQLite)"),
        ("DB\n(SQLite)", "Cash & Report Tool\n(get_cash_balance /\ngenerate_financial_report)"),
    ]

    node_types = {
        "Customer Inquiry": "user",
        "Orchestrator Agent": "agent",
        "Inventory Agent": "agent",
        "Quoting Agent": "agent",
        "Transaction Agent": "agent",
        "Check Inventory Tool\n(get_all_inventory /\nget_stock_level)": "tool",
        "Supplier Delivery Tool\n(get_supplier_delivery_date)": "tool",
        "Quote History Tool\n(search_quote_history)": "tool",
        "Discount & Pricing Tool\n(paper_supplies + bulk tiers)": "tool",
        "Fulfill Order Tool\n(create_transaction:\nsales & stock_orders)": "tool",
        "Cash & Report Tool\n(get_cash_balance /\ngenerate_financial_report)": "tool",
        "DB\n(SQLite)": "data"
    }

    edge_labels = {
        ("Customer Inquiry", "Orchestrator Agent"): "Inquiry + Date",
        ("Orchestrator Agent", "Customer Inquiry"): "Final Quote / Receipt",
        ("Orchestrator Agent", "Inventory Agent"): "1. Check Stock & Lead Time",
        ("Orchestrator Agent", "Quoting Agent"): "2. Calculate Quote & Discount",
        ("Orchestrator Agent", "Transaction Agent"): "3. Fulfill Sale / Restock Order"
    }

    create_diagram(
        "Beaver's Choice Paper Company: Multi-Agent Workflow",
        nodes,
        edges,
        None,
        node_types,
        edge_labels
    )


if __name__ == "__main__":
    beavers_choice_solution()
