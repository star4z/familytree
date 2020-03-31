data = JSON.parse(document.getElementById('data').textContent);

console.log(data);

const graph = new G6.Graph({
    container: "family-graph",
    width: 500,
    height: 500,
});

graph.data(data);
graph.render();