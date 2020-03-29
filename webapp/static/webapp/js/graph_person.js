let person_id = JSON.parse(document.getElementById('person_id').textContent);
let persons = JSON.parse(document.getElementById('persons').textContent);

console.log(persons);

let person = persons[person_id];

const data = {
    nodes: [],
    edges: []
};


data.nodes.push({
    id: person.id.toString(),
    x: 0,
    y: 0
});

added_people = [person_id];

for (let m_person of Object.values(persons)) {
    if (!(added_people.includes(m_person.id))) {
        for (let m_partnership of m_person.partnerships) {
            if (m_partnership.children.includes(person.id)) {
                added_people.push(m_person.id);
                console.log(data.nodes);
                data.nodes.push({
                        id: m_person.id.toString(),
                        x: -50,
                        y: -50
                    },
                    {
                        id: 'p' + person.id.toString(),
                        x: 0,
                        y: -50
                    }
                );
                console.log(data.nodes);
                data.edges.push(
                    {
                        source: person.id.toString(),
                        target: 'p' + person.id.toString(),
                    },
                    {
                        source: m_person.id.toString(),
                        target: 'p' + person.id.toString()
                    }
                );
                if (m_partnership.partners.length !== 0) {
                    let m_partner = m_partnership.partners[0];
                    data.nodes.push({
                        id: m_partner.toString(),
                        x: 50,
                        y: -50
                    });
                    data.edges.push({
                       source: m_partner.toString(),
                       target: 'p' + person.id.toString()
                    });
                    added_people.push(m_partner);
                }
            }
        }
    }
}

let minX = 0;
let minY = 0;
//Find minX and minY
for (let node of data.nodes) {
    if (node.x < minX) {
        minX = node.x;
    }
    if (node.y < minY) {
        minY = node.Y;
    }
}

//Shift all nodes to make all values positive
for (let node of data.nodes) {
    node.x += 50 - minX;
    node.y += 50 - minY;
}

const graph = new G6.Graph({
    container: "family-graph",
    width: 500,
    height: 500,
});

console.log(data);

graph.data(data);
graph.render();