import ast
import networkx as nx
import gravis as gv
from queue import Queue
from collections import defaultdict

PROJECT_PATH = "./Loop-Labyrinth-Analysis-main/"
ENTRY_POINT = "app"

def get_imports(tree):
  imports = []
  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      for alias in node.names:
        imports.append([alias.name])
    elif isinstance(node, ast.ImportFrom):
      module = node.module
      imports.append([module])
      # for alias in node.names:
        # imports.append([module, alias.name])
  return imports
  
def construct_import_adj(entry_point_file):
  queue = Queue()
  queue.put([entry_point_file])
  adj_list = defaultdict(set)
  visited = set()
  while not queue.empty():
    file = queue.get()
    filename = file[0].replace(".", "/")
    try:
      f = open(f"{PROJECT_PATH}/{filename}.py", "r")
    except FileNotFoundError:
      # External library
      continue
    f_data = f.read()
    tree = ast.parse(f_data, filename=filename)
    imports = get_imports(tree)
    for imp in imports:
      fmt_import = ".".join(imp)
      print(f"{file[0]} -> {fmt_import}")
      adj_list[file[0]].add(fmt_import)
      if fmt_import not in visited:
        visited.add(fmt_import)
        queue.put(imp)
  return adj_list

def visualize(graph):
  G = nx.DiGraph()
  for node in graph:
    G.add_node(node)
    for edge in graph[node]:
      G.add_edge(node, edge)
  centrality = nx.degree_centrality(G)
  communities = nx.algorithms.community.greedy_modularity_communities(G)
  nx.set_node_attributes(G, centrality, "size")
  colors = ['red', 'blue', 'green', 'orange', 'pink']
  for community, color in zip(communities, colors):
      for node in community:
          G.nodes[node]['color'] = color
  fig = gv.d3(G, use_node_size_normalization=True, node_size_normalization_max=30, use_edge_size_normalization=True, edge_size_data_source="weight", edge_curvature=0.3, edge_label_data_source="en")
  fig.display()

if __name__ == "__main__":
  graph = construct_import_adj(ENTRY_POINT)
  print(graph)
  visualize(graph)
