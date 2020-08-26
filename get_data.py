import requests
import json
import csv
import networkx as nx
import matplotlib.pyplot as plt
from operator import itemgetter

graph = nx.Graph()


def write_tags_to_file(tags):
    with open('tags.csv', 'a') as result_file:
        wr = csv.writer(result_file, dialect='excel')
        wr.writerow(tags)


def fetch_tags_from_web():
    items = range(100)
    page_numbers = range(1, 254)

    for page_number in page_numbers:
        for i in items:
            # print('Reading page %d, item number %d' %(page_number, items))
            url = 'https://api.stackexchange.com/2.2/questions?page=' + str(
                page_number) + '&pagesize=100&order=desc&sort=activity&site=datascience&key=alcODF*i94yom4TuEuPhAA(('
            response = requests.get(url=url)
            if response.ok:
                json_data = response.json()
                d = json.loads(json.dumps(json_data))
                tag = d['items'][i]['tags']
                write_tags_to_file(tag)
            else:
                print(response.status_code)
                print('Page number: %d, items: %d' % (page_number, items))
                break


def read_tags_from_file():
    all_tags = []
    with open('tags.csv', 'r') as r:
        reader = csv.reader(r)
        for line in reader:
            all_tags.append(line)
    return all_tags


def build_tags_graph():
    all_tag_sets = read_tags_from_file()
    all_tag_sets = all_tag_sets[:10]
    nodes_in_graph = []
    for tag_set in all_tag_sets:
        for tag in tag_set:
            if tag not in nodes_in_graph:
                graph.add_node(tag)
                nodes_in_graph.append(tag)
            if len(nodes_in_graph) > 1:
                for node in nodes_in_graph:
                    if not graph.has_edge(tag, node):
                        graph.add_edge(tag, node, weight=1)
                    else:
                        graph[tag][node]["weight"] += 1


def plot_graph():
    plt.figure(figsize=(50, 50))
    e_list = [(u, v) for (u, v, d) in graph.edges(data=True)]
    pos = nx.spring_layout(graph)
    # nodes
    nx.draw_networkx_nodes(graph, pos, node_size=500)

    # edges
    nx.draw_networkx_edges(graph, pos, edgelist=e_list, width=1)

    # labels
    nx.draw_networkx_labels(
        graph, pos, font_size=8, font_family='sans-serif')
    plt.axis('off')
    plt.show()


def find_neighboring_tags(tag):
    neighbors = graph.neighbors(tag)
    all_neighbors = []
    for neighbor in neighbors:
        n = graph.get_edge_data(tag, neighbor)
        all_neighbors.append([neighbor, n['weight']])
    return all_neighbors


def sort_neighboring_tags(neightboring_tags):
    return sorted(neightboring_tags, key=itemgetter(1), reverse=True)


def get_n_most_related_tags(sorted_tags, n):
    return sorted_tags[:n]


def display_suggested_tags(highly_related_tags):
    for tags in highly_related_tags:
        print('%s | ' % (tags[0]),end=""),


build_tags_graph()
neighboring_tags = find_neighboring_tags('scikit-learn')
sorted_tags = sort_neighboring_tags(neighboring_tags)
highly_related_tags = get_n_most_related_tags(sorted_tags, 10)
display_suggested_tags(highly_related_tags)

plot_graph()
