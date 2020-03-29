let person_id = JSON.parse(document.getElementById('person_id').textContent);
let persons = JSON.parse(document.getElementById('persons').textContent);

console.log(persons);

let person = persons[person_id];
//
// function getOldest(pid) {
//     let older = [];
//     for (let parent of persons[pid].parents) {
//         //TODO: check for circular trees
//         if (parent.id in persons) {
//             older.push(parent.id);
//         }
//     }
//     if (older.length !== 0) {
//         let oldest = [];
//         for (let person of older) {
//             let elder = getOldest(person);
//             oldest = oldest.concat(elder);
//         }
//         return oldest;
//     } else {
//         return [pid];
//     }
// }
//
// let oldest = getOldest(person_id);
//
// console.log(oldest);

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
    for (let m_partnership of m_person.partnerships) {
        if (person.id in m_partnership.children) {
            data.nodes.push({
                    id: m_person.id.toString(),
                    x: -50,
                    y: -50
                },
                {
                    id: 'p' + person.id.toString(),
                    x: 50,
                    y: -75
                }
            );
            data.edges.push(
                {
                    source: person.id.toString(),
                    target: 'p' + person.id.toString(),
                },
                {
                    source: m_person.id.toString(),
                    target: 'p' + person.id.toString()
                });
        }
    }
}
//
// for (let i of oldest) {
//     let x = 0;
//     data.nodes.push({
//         id: persons[i].name,
//         x: x,
//         y: 0,
//     });
//     data.edges.push({
//         source: persons[i].name,
//     });
//     x += 100;
// }

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
    width: 800,
    height: 500,
});

graph.data(data);
graph.render();