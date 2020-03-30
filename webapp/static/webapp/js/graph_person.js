//Declaring types for type hint purposes
let persons = [{model: null, pk: null, fields: {legal_name: null}}];
let person_partnerships = [{model: null, pk: null, fields: {person: null, partnership: null}}];
let partnerships = [{model: null, pk: null, fields: {children: []}}];
let legal_names = [{model: null, pk: null, fields: {first_name: null, last_name: null}}];

person_id = JSON.parse(document.getElementById('person_id').textContent);
persons = JSON.parse(JSON.parse(document.getElementById('persons').textContent));
person_partnerships = JSON.parse(JSON.parse(document.getElementById('person_partnerships').textContent));
partnerships = JSON.parse(JSON.parse(document.getElementById('partnerships').textContent));
legal_names = JSON.parse(JSON.parse(document.getElementById('legal_names').textContent));

console.log(person_id);
console.log(persons);
console.log(person_partnerships);
console.log(partnerships);
console.log(legal_names);


function getPerson(pk) {
    for (let person of persons) {
        // console.log(person);
        if (person.pk === pk) {
            return person
        }
    }
}

function getName(person) {
    for (let name of legal_names) {
        if (name.pk === person.fields.legal_name) {
            return name
        }
    }
}

function prettyPrintName(name) {
    return name.fields.first_name + " " + name.fields.last_name
}

function getPartnership(pk) {
    for (let partnership of partnerships) {
        if (partnership.pk === pk) {
            return partnership;
        }
    }
}

function getPartnerships(person) {
    let partnerships = [];
    for (let person_partnership of person_partnerships) {
        if (person_partnership.fields.person === person.pk) {
            partnerships.push(getPartnership(person_partnership.fields.partnership));
        }
    }
    return partnerships;
}

Array.prototype.exclude = function (pk) {
    let array = [];
    for (let i of this) {
        if (i.pk !== pk) {
            array.push(i);
        }
    }
    return array;
};

function getPartners(partnership) {
    let persons = [];
    for (let person_partnership of person_partnerships) {
        if (person_partnership.fields.partnership === partnership.pk) {
            persons.push(getPerson(person_partnership.fields.person));
        }
    }
    return persons;
}

let person = getPerson(person_id);

console.log(prettyPrintName(getName(person)));

const data = {
    nodes: [],
    edges: []
};

function personId(person) {
    return 'person_' + person.pk.toString();
}

function partnershipId(partnership) {
    return 'partnership_' + partnership.pk.toString();
}

function childId(person) {
    return 'child_' + person.pk.toString();
}

function midPointId(partnership) {
    return 'midpoint_' + partnership.pk.toString();
}

function getNode(id) {
    for (let node of data.nodes) {
        if (node.id === id) {
            return node;
        }
    }
}

data.nodes.push({
    id: personId(person),
    x: 0,
    y: 0
});

added_people = [person_id];

for (let m_person of persons) {
    if (!(added_people.includes(m_person.pk))) {
        for (let m_partnership of getPartnerships(m_person)) {
            if (m_partnership.fields.children.includes(person.pk)) {
                added_people.push(m_person.pk);
                data.nodes.push({
                        id: personId(m_person),
                        x: -50,
                        y: -50
                    },
                    {
                        id: partnershipId(m_partnership),
                        x: 0,
                        y: -50
                    }
                );
                data.edges.push(
                    {
                        source: personId(person),
                        target: partnershipId(m_partnership),
                    },
                    {
                        source: personId(m_person),
                        target: partnershipId(m_partnership)
                    }
                );
                let m_partners = getPartners(m_partnership);
                if (m_partners.length !== 0) {
                    let m_partner = m_partners[0];
                    data.nodes.push({
                        id: personId(m_partner),
                        x: 50,
                        y: -50
                    });
                    data.edges.push({
                        source: personId(m_partner),
                        target: partnershipId(m_partnership)
                    });
                    added_people.push(m_partner);
                }
            }
        }
    }
}

for (let m_partnership of getPartnerships(person)) {
    for (let m_partner of getPartners(m_partnership)) {
        if (!(added_people.includes(m_partner.pk))) {
            data.nodes.push({
                id: personId(m_partner),
                x: 100,
                y: 0
            }, {
                id: partnershipId(m_partnership),
                x: 50,
                y: 0
            });
            data.edges.push({
                source: personId(person),
                target: partnershipId(m_partnership)
            }, {
                source: personId(m_partner),
                target: partnershipId(m_partnership)
            });
            added_people.push(m_partner);
        }
    }
    let n = m_partnership.fields.children.length;
    let offset = getNode(partnershipId(m_partnership)).x;
    if (n > 0) {
        for (let i = 0; i < n; i++) {
            let m_child = getPerson(m_partnership.fields.children[i]);
            if (!(added_people.includes(m_child))) {
                let xi = -25 * (n - 1) + 50 * i + offset;
                data.nodes.push({
                    id: personId(m_child),
                    x: xi,
                    y: 50
                }, {
                    id: childId(m_child),
                    x: xi,
                    y: 25
                });
                data.edges.push({
                    source: childId(m_child),
                    target: personId(m_child)
                });
                if (i > 0) {
                    data.edges.push({
                        source: childId(m_child),
                        target: childId(getPerson(m_partnership.fields.children[i - 1]))
                    })
                }
                added_people.push(m_child);
            }
        }
        data.nodes.push({
            id: midPointId(m_partnership),
            x: offset,
            y: 25
        });
        data.edges.push({
            source: partnershipId(m_partnership),
            target: midPointId(m_partnership)
        });
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
        minY = node.y;
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