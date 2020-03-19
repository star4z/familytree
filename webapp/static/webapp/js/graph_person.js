person_id = JSON.parse(document.getElementById('person_id').textContent);
persons = JSON.parse(document.getElementById('persons').textContent);

person = persons[person_id];

person_box = {height: 30, width: 100};
box_padding = {vert: 10, horiz: 10};

const sum = (a, b) => a + b;

/**
 * Contains an array of Items to be graphed at roughly the same y-value.
 */
class Row {
    constructor(contents) {
        this.contents = contents;
    }

    width = function () {
        return this.contents.map(item => item.full_width()).reduce(sum);
    };

    height = function() {
        return Math.max(this.contents.map(item => item.full_height()));
    };
}

/**
 * Contains values and type info for graphing
 */
class Item {
    constructor() {
        //Define defaults. These should not be overwritten. These values can be used to inform the actual values.
        this.defaults = {};
        this.defaults.padding = {top: 10, right: 10, bottom: 10, left: 10};
        this.defaults.width = 100;
        this.defaults.height = 30;

        //Set these values in instances to manipulate.
        this.padding = {};
        Object.assign(this.padding, this.defaults.padding);
        this.width = this.defaults.width;
        this.height = this.defaults.height;
    }

    full_width() {
        return this.padding.left + this.width + this.padding.right;
    };

    full_height() {
        return this.padding.top + this.height + this.padding.bottom;
    };

    graph(x, y, ctx) {
    }
}

class Partnership extends Item {
    constructor(partners, children) {
        super();
        this.partners = partners;
        this.children = children;
    }

    full_width() {
        return 2 * super.full_width();
    }

    graph(x, y, ctx) {
        const offset1 = {x: x + this.padding.left, y: y + this.padding.top};
        ctx.fillRect(offset1.x, offset1.y, this.defaults.width, this.height);
        const offset2 = {
            x: x + this.padding.left + this.defaults.width + this.padding.right + this.padding.left,
            y: y + this.padding.top
        };
        ctx.fillRect(offset2.x, offset2.y, this.width, this.height);
        ctx.moveTo(x + this.padding.left + this.width, y + this.padding.top + this.height / 2);
        ctx.lineTo(x + 2 * this.padding.left + this.padding.right + this.width, y + this.padding.top + this.height / 2);
        ctx.stroke();
    }
}

class Person extends Item {
    constructor(id) {
        super();
        this.id = id;
    }

    graph(x, y, ctx) {
        ctx.fillRect(x + this.padding.left, y + this.padding.top, this.width, this.height);
    }
}

let person_partners = [];
let children = [];
for (let partnership of person.partnerships) {
    person_partners = person_partners.concat(partnership.partners);
    children = children.concat(partnership.children);
}
person_partners.push(person.id);

rows = [
    new Row([
        new Partnership(person.parents, [person.id]),
    ]),
    new Row([
        new Partnership(person_partners, children),
    ]),
    new Row(
        children.map(child => new Person(child))
    ),
];

canvas = document.getElementById("person-graph");
ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let y = 0;
for (let row of rows) {
    let x = 0;
    for (item of row.contents) {
        item.graph(x, y, ctx);
        x += item.full_width();
    }
    y += row.height();
}