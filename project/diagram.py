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

    plt.figure(figsize=(16, 11))
    plt.title(title, fontsize=16, fontweight='bold', pad=20)

    pos = {}
    horizontal_spacing = 1.4
    vertical_spacing = 1.0

    # Column 0: User Interface
    pos["Customer Inquiry"] = (0, 0)

    # Column 1: Orchestrator Agent
    pos["Orchestrator Agent"] = (1 * horizontal_spacing, 0)

    # Column 2: Specialized Worker Agents
    pos["Inventory Agent"] = (2 * horizontal_spacing, 1.35 * vertical_spacing)
    pos["Quoting Agent"] = (2 * horizontal_spacing, 0)
    pos["Transaction Agent"] = (2 * horizontal_spacing, -1.35 * vertical_spacing)

    # Column 3: Starter Code Helper Function Tools (all 7 functions mapped)
    pos["get_all_inventory\n(Full Stock Snapshot)"] = (3.25 * horizontal_spacing, 2.1 * vertical_spacing)
    pos["get_stock_level\n(Item Stock Check)"] = (3.25 * horizontal_spacing, 1.4 * vertical_spacing)
    pos["get_supplier_delivery_date\n(Supplier Lead Time)"] = (3.25 * horizontal_spacing, 0.7 * vertical_spacing)

    pos["search_quote_history\n(Historical Quotes & Pricing)"] = (3.25 * horizontal_spacing, 0.0)

    pos["create_transaction\n(Record Sales & Stock Orders)"] = (3.25 * horizontal_spacing, -0.7 * vertical_spacing)
    pos["get_cash_balance\n(Check Available Cash)"] = (3.25 * horizontal_spacing, -1.4 * vertical_spacing)
    pos["generate_financial_report\n(Assets & Best-Sellers Report)"] = (3.25 * horizontal_spacing, -2.1 * vertical_spacing)

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

        # Agents (4 total <= 5 limit)
        "Orchestrator Agent",
        "Inventory Agent",
        "Quoting Agent",
        "Transaction Agent",

        # Inventory Agent Tools (Starter Code Helper Functions)
        "get_all_inventory\n(Full Stock Snapshot)",
        "get_stock_level\n(Item Stock Check)",
        "get_supplier_delivery_date\n(Supplier Lead Time)",

        # Quoting Agent Tools (Starter Code Helper Functions)
        "search_quote_history\n(Historical Quotes & Pricing)",

        # Transaction Agent Tools (Starter Code Helper Functions)
        "create_transaction\n(Record Sales & Stock Orders)",
        "get_cash_balance\n(Check Available Cash)",
        "generate_financial_report\n(Assets & Best-Sellers Report)",

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

        # Inventory Agent <-> Starter Helper Tools
        ("Inventory Agent", "get_all_inventory\n(Full Stock Snapshot)"),
        ("get_all_inventory\n(Full Stock Snapshot)", "Inventory Agent"),
        ("Inventory Agent", "get_stock_level\n(Item Stock Check)"),
        ("get_stock_level\n(Item Stock Check)", "Inventory Agent"),
        ("Inventory Agent", "get_supplier_delivery_date\n(Supplier Lead Time)"),
        ("get_supplier_delivery_date\n(Supplier Lead Time)", "Inventory Agent"),

        # Quoting Agent <-> Starter Helper Tools
        ("Quoting Agent", "search_quote_history\n(Historical Quotes & Pricing)"),
        ("search_quote_history\n(Historical Quotes & Pricing)", "Quoting Agent"),

        # Transaction Agent <-> Starter Helper Tools
        ("Transaction Agent", "create_transaction\n(Record Sales & Stock Orders)"),
        ("create_transaction\n(Record Sales & Stock Orders)", "Transaction Agent"),
        ("Transaction Agent", "get_cash_balance\n(Check Available Cash)"),
        ("get_cash_balance\n(Check Available Cash)", "Transaction Agent"),
        ("Transaction Agent", "generate_financial_report\n(Assets & Best-Sellers Report)"),
        ("generate_financial_report\n(Assets & Best-Sellers Report)", "Transaction Agent"),

        # Tools <-> SQLite Database
        ("get_all_inventory\n(Full Stock Snapshot)", "DB\n(SQLite)"),
        ("DB\n(SQLite)", "get_all_inventory\n(Full Stock Snapshot)"),
        ("get_stock_level\n(Item Stock Check)", "DB\n(SQLite)"),
        ("DB\n(SQLite)", "get_stock_level\n(Item Stock Check)"),
        ("search_quote_history\n(Historical Quotes & Pricing)", "DB\n(SQLite)"),
        ("DB\n(SQLite)", "search_quote_history\n(Historical Quotes & Pricing)"),
        ("create_transaction\n(Record Sales & Stock Orders)", "DB\n(SQLite)"),
        ("get_cash_balance\n(Check Available Cash)", "DB\n(SQLite)"),
        ("DB\n(SQLite)", "get_cash_balance\n(Check Available Cash)"),
        ("generate_financial_report\n(Assets & Best-Sellers Report)", "DB\n(SQLite)"),
        ("DB\n(SQLite)", "generate_financial_report\n(Assets & Best-Sellers Report)"),
    ]

    node_types = {
        "Customer Inquiry": "user",
        "Orchestrator Agent": "agent",
        "Inventory Agent": "agent",
        "Quoting Agent": "agent",
        "Transaction Agent": "agent",
        "get_all_inventory\n(Full Stock Snapshot)": "tool",
        "get_stock_level\n(Item Stock Check)": "tool",
        "get_supplier_delivery_date\n(Supplier Lead Time)": "tool",
        "search_quote_history\n(Historical Quotes & Pricing)": "tool",
        "create_transaction\n(Record Sales & Stock Orders)": "tool",
        "get_cash_balance\n(Check Available Cash)": "tool",
        "generate_financial_report\n(Assets & Best-Sellers Report)": "tool",
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
