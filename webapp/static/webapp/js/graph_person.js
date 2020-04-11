data = JSON.parse(document.getElementById('data').textContent);
width = JSON.parse(document.getElementById('width').textContent);
height = JSON.parse(document.getElementById('height').textContent);

console.log(data);


G6.registerBehavior('activate-node', {
    getEvents() {
        return {
            'node:click': 'onNodeClick',
        };
    },
    onNodeClick(e) {
        const item = e.item;
        console.log(item);
        let id_pieces = item._cfg.id.split('_');
        if (id_pieces.length === 2 && id_pieces[0] === 'Person') {
            let link = id_pieces[id_pieces.length - 1];
            window.location = '/webapp/person/' + link + '/graph/';
        }
    }
});

const graph = new G6.Graph({
    container: "family-graph",
    width: width,
    height: height,
    modes: {
        default: ['activate-node'],
    },
});

console.log(graph);

graph.data(data);
graph.render();