import io
from flask import Flask, request, jsonify, render_template_string, send_file
from matplotlib import pyplot as plt
import networkx as nx
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

# Граф задач и серверов
clients = ['C1', 'C2', 'C3', 'C4', 'C5']
servers = ['S1', 'S2', 'S3']
edges = [('C1', 'S1'), ('C2', 'S1'), ('C3', 'S1'), ('C4', 'S1'), ('C5', 'S1'),         ('C1', 'S2'), ('C2', 'S2'), ('C3', 'S2'), ('C4', 'S2'), ('C5', 'S2'),         ('C1', 'S3'), ('C2', 'S3'), ('C3', 'S3'), ('C4', 'S3'), ('C5', 'S3'),         ('C1', 'C2'), ('C1', 'C3'), ('C2', 'C4'), ('C3', 'C4')]


# Создание двудольного графа
B = nx.Graph()
B.add_nodes_from(clients, bipartite=0)
B.add_nodes_from(servers, bipartite=1)
B.add_edges_from(edges)

# Алгоритм Хопкрофта-Карпа
def hopcroft_karp(B):
    matching = {}
    while True:
        levels = bfs_levels(B, matching)
        if not levels:
            break
        for client in sorted(clients):
            if client not in matching:
                if dfs_augmenting_path(B, matching, client, levels):
                    continue
    return matching

def bfs_levels(B, matching):
    levels = {}
    queue = []
    for client in sorted(clients):
        if client not in matching:
            levels[client] = 0
            queue.append(client)
    found = False
    while queue:
        client = queue.pop(0)
        for server in sorted(B.neighbors(client)):
            matched_client = matching.get(server)
            if matched_client is None:
                found = True
            elif matched_client not in levels:
                levels[matched_client] = levels[client] + 1
                queue.append(matched_client)
    return levels if found else None

def dfs_augmenting_path(B, matching, client, levels):
    for server in sorted(B.neighbors(client)):
        matched_client = matching.get(server)
        if matched_client is None or (levels[matched_client] == levels[client] + 1 and dfs_augmenting_path(B, matching, matched_client, levels)):
            matching[server] = client
            matching[client] = server
            return True
    return False

@app.route('/assign_tasks', methods=['POST'])
def assign_tasks():
    app.logger.debug("Received POST request at /assign_tasks")
    matching = hopcroft_karp(B)
    app.logger.debug(f"Matching result: {matching}")
    response = jsonify(matching)
    app.logger.debug(f"Response: {response.get_data(as_text=True)}")
    return response

@app.route('/graph_data', methods=['GET'])
def graph_data():
    matching = hopcroft_karp(B)
    matching_edges = [(u, v) for u, v in matching.items() if u in clients]
    data = {
        "nodes": [{"id": n, "group": 0 if n in clients else 1} for n in B.nodes()],
        "links": [{"source": u, "target": v, "matched": (u, v) in matching_edges or (v, u) in matching_edges} for u, v in B.edges()]
    }
    return jsonify(data)

@app.route('/view_graph', methods=['GET'])
def view_graph():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Graph Visualization</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            .node circle {
                stroke: #fff;
                stroke-width: 1.5px;
            }
            .node text {
                font: 10px sans-serif;
            }
            .link {
                stroke: #999;
                stroke-opacity: 0.6;
            }
            .matched {
                stroke: #ff0000;
                stroke-width: 2.5px;
            }
        </style>
    </head>
    <body>
        <h1>Graph Visualization</h1>
        <div id="graph"></div>
        <script>
            const width = 1200;
            const height = 900;

            const svg = d3.select("#graph").append("svg")
                .attr("width", width)
                .attr("height", height);

            d3.json("{{ url_for('graph_data') }}").then(data => {
                const simulation = d3.forceSimulation(data.nodes)
                    .force("link", d3.forceLink(data.links).id(d => d.id).distance(200))
                    .force("charge", d3.forceManyBody().strength(-400))
                    .force("center", d3.forceCenter(width / 2, height / 2));

                const link = svg.append("g")
                    .attr("class", "links")
                    .selectAll("line")
                    .data(data.links)
                    .enter().append("line")
                    .attr("class", d => d.matched ? "link matched" : "link")
                    .attr("stroke-width", 2);

                const node = svg.append("g")
                    .attr("class", "nodes")
                    .selectAll("g")
                    .data(data.nodes)
                    .enter().append("g");

                node.append("circle")
                    .attr("r", 10)
                    .attr("fill", d => d.group === 0 ? "lightgreen" : "lightcoral")
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));

                node.append("text")
                    .attr("x", 12)
                    .attr("dy", ".35em")
                    .text(d => d.id);

                simulation
                    .nodes(data.nodes)
                    .on("tick", ticked);

                simulation.force("link")
                    .links(data.links);

                function ticked() {
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);

                    node
                        .attr("transform", d => `translate(${d.x},${d.y})`);
                }

                function dragstarted(event, d) {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }

                function dragged(event, d) {
                    d.fx = event.x;
                    d.fy = event.y;
                }

                function dragended(event, d) {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }
            });
        </script>
    </body>
    </html>
    ''')
@app.route('/visualize_graph', methods=['GET'])
def visualize_graph():
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(B)
    nx.draw(B, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=15, font_weight='bold')
    nx.draw_networkx_nodes(B, pos, nodelist=clients, node_color='lightgreen', node_size=2000)
    nx.draw_networkx_nodes(B, pos, nodelist=servers, node_color='lightcoral', node_size=2000)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)



