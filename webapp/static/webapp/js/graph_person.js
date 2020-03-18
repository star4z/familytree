person_id = JSON.parse(document.getElementById('person_id').textContent);
persons = JSON.parse(document.getElementById('persons').textContent);

console.log(person_id);
console.log(persons);

person_box = {"height": 30, width: 100};

canvas = document.getElementById("person-graph");
ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
ctx.fillStyle = "#FF0000";
ctx.moveTo(0, 0);
ctx.lineTo(500, 500);
ctx.stroke();
// ctx.fillRect(0, 0, 500, 500);