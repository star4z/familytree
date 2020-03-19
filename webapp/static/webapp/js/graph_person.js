person_id = JSON.parse(document.getElementById('person_id').textContent);
persons = JSON.parse(document.getElementById('persons').textContent);

console.log(person_id);
console.log(persons);

person = persons[person_id];

person_box = {height: 30, width: 100};
box_padding = {vert: 10, horiz: 10};

//row width = length of the box for each person in the row, plus the padding between them.
row0_width = person.parents.length * person_box.width + 2 * (person.parents.length - 1) * box_padding.horiz;
row1_width = person_box.width + person.partnerships.length * (person_box.width + 2 * box_padding.horiz);
num_children = 0;
for (partnership of person.partnerships) {
    num_children += partnership.children.length;
}
row2_width = num_children * person_box.width + (num_children - 1) * box_padding.horiz;

console.log(row0_width);
console.log(row1_width);
console.log(row2_width);

row0_start = 0;
row1_start = row0_start + (row0_width - person_box.width) / 2;
row2_start = row1_start + (row1_width - row2_width) / 2;
min_start = Math.min(row0_start, row1_start, row2_start);
row0_start -= min_start;
row1_start -= min_start;
row2_start -= min_start;

console.log(row0_start);
console.log(row1_start);
console.log(row2_start);

row0_y = 0;
row1_y = row0_y + person_box.height + box_padding.vert;
row2_y = row1_y + person_box.height + 2 * box_padding.vert;

canvas = document.getElementById("person-graph");
ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// ctx.fillStyle = "#FF0000";
x = row0_start;
for (parent of person.parents) {
    ctx.fillRect(x, row0_y, person_box.width, person_box.height);
    x += person_box.width + 2 * box_padding.horiz;
}
x = row1_start;
ctx.fillRect(x, row1_y, person_box.width, person_box.height);
x += person_box.width + 2 * box_padding.horiz;
for (partnership of person.partnerships) {
    for (partner of partnership.partners) {
        ctx.fillRect(x, row1_y, person_box.width, person_box.height);
        x += person_box.width + 2 * box_padding.horiz;
    }
}
x = row2_start;
for (partnership of person.partnerships) {
    for (child of partnership.children) {
        ctx.fillRect(x, row2_y, person_box.width, person_box.height);
        x += person_box.width + 2 * box_padding.horiz;
    }
}
// ctx.moveTo(0, 0);
// ctx.lineTo(500, 500);
// ctx.stroke();
// ctx.fillRect(0, 0, 500, 500);