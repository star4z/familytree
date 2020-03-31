data = JSON.parse(document.getElementById('data').textContent);

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
    width: 500,
    height: 500,
    modes: {
        default: ['activate-node'],
    },
});

graph.data(data);
graph.render();