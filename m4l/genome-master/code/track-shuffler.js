var ons = [];
var offs = [1, 2, 3, 4, 5, 6, 7];

function density(d) {
	if (d > ons.length && offs.length > 0) {
		turn_one_on();
	} else if (d < ons.length && ons.length > 0) {
		turn_one_off();
	} else {
		if (offs.length == 0) {
			turn_one_off();
			turn_one_on();
		} else {
			turn_one_on();
			turn_one_off();
		}
	}
	dump();
}

function turn_one_on() {
	var ridx = Math.floor(Math.random()*offs.length);
	var new_on = offs.splice(ridx, 1)[0];
	ons.push(new_on);
}

function turn_one_off() {
	var ridx = Math.floor(Math.random()*ons.length);
	var new_off = ons.splice(ridx, 1)[0];
	offs.push(new_off);
}

function dump() {
	for (var i=0; i<ons.length; i++) {
		outlet(0, ons[i], 1);
	}
	for (var i=0; i<offs.length; i++) {
		outlet(0, offs[i], 0);
	}
}

function all_on() {
	ons = [1, 2, 3, 4, 5, 6, 7];
	offs = [];
	dump();
}