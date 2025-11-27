"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import pipmaster as pm

if not pm.is_installed("pyvis"):
    pm.install("pyvis")
if not pm.is_installed("networkx"):
    pm.install("networkx")
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UXpka1JBPT06YTNhNDkyNTE=

import networkx as nx
from pyvis.network import Network
import random

# Load the GraphML file
G = nx.read_graphml("./dickens/graph_chunk_entity_relation.graphml")

# Create a Pyvis network
net = Network(height="100vh", notebook=True)

# Convert NetworkX graph to Pyvis network
net.from_nx(G)
# noqa  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UXpka1JBPT06YTNhNDkyNTE=


# Add colors and title to nodes
for node in net.nodes:
    node["color"] = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    if "description" in node:
        node["title"] = node["description"]

# Add title to edges
for edge in net.edges:
    if "description" in edge:
        edge["title"] = edge["description"]

# Save and display the network
net.show("knowledge_graph.html")
