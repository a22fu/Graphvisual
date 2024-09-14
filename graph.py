import ast
import networkx as nx
import os
import matplotlib.pyplot as plt
import mplcursors


def parse(network, path, fromdict, node_types):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if filename.endswith(".py"):
            node_types[filename] = 'Python File'
            with open(file_path, encoding='utf-8') as file:
                code = file.read()
                node = ast.parse(code)
                body = node.body
                for x in body:
                    imported_names = []
                    if isinstance(x, ast.ImportFrom):
                        for alias in x.names:
                            imported_names.append(alias.name)
                        fromdict[x] = imported_names
                        network.add_edge(filename, x.module)
                        node_types[x.module] = 'Module'
                    elif isinstance(x, ast.Import):
                        for alias in x.names:
                            network.add_edge(filename, alias.name)
                            node_types[alias.name] = 'Module'
        elif os.path.isdir(file_path) and not file_path.endswith(".git"):
            parse(network, file_path, fromdict, node_types)
        else:
            node_types[filename] = 'Other'


# Main section of the script
if __name__ == '__main__':
    path = input("Enter your repo path!")
    network = nx.Graph()
    fromdict = dict()
    node_types = dict()
    parse(network, path, fromdict, node_types)

    color_map = {
        'Python File': 'skyblue',
        'Module': 'lightgreen',
        'Other': 'lightcoral'
    }

    node_colors = [color_map.get(node_types.get(node, 'Other'), 'gray') for node in network.nodes()]

    pos = nx.spring_layout(network, seed=42)

    # Draw the graph
    nodes = nx.draw_networkx_nodes(network, pos, node_color=node_colors, node_size=100, alpha=0.9)
    nx.draw_networkx_edges(network, pos, width=1, edge_color='gray', alpha=0.6)

    # Draw node labels but set them invisible initially
    labels = nx.draw_networkx_labels(network, pos, font_size=10, font_color='black', font_weight='bold')
    for label in labels.values():
        label.set_visible(False)  # Hide labels initially

    # Manual legend
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=label,
                          markersize=10, markerfacecolor=color)
               for label, color in color_map.items()]
    plt.legend(handles=handles, title='Node Types')

    # Customize plot appearance
    plt.title("Network Graph with Node Types")
    plt.axis('equal')  # Ensure equal scaling of x and y axes

    # Enable hover interaction for node names
    cursor = mplcursors.cursor(nodes, hover=True)


    @cursor.connect("add")
    def on_add(sel):
        node_index = sel.index
        node_name = list(network.nodes())[node_index]
        # Make the label visible only for the hovered node
        label = list(labels.values())[node_index]
        label.set_text(node_name)
        label.set_visible(True)
        sel.annotation.set(text=node_name, fontsize=12)


    @cursor.connect("remove")
    def on_remove(sel):
        # Hide all labels when hover is removed
        for label in labels.values():
            label.set_visible(False)


    # Show the graph with customizations
    plt.show()
