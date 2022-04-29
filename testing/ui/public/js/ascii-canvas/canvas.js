const { Canvas, Item } = canvas;

var text, height, width, box, angle, cursor, world, robot;

const ROWS = 18;
const COLS = 80;
const myCanvas = new Canvas(COLS, ROWS);

const rect = new Item(frame());
myCanvas.append(rect);



function rep(str, count) {
    return new Array(count).fill(str).join('');
}

function frame() {
    const output = [];
    const x_count = COLS - 2;
    const y_Count = ROWS - 2;
    output.push(`+${rep('-', x_count)}+`);
    for (let i = 0; i < y_Count; ++i) {
        output.push(`|${rep(' ', x_count)}|`);
    }
    output.push(`+${rep('-', x_count)}+`);
    return output.join('\n');
}

function rotation_ascii(angle) {
    const ascii = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖'];

    // compute compass direction (N, NE, E, SE, S, SW, W, NW) closest to current angle.
    let index = Math.round(((angle %= 360) < 0 ? angle + 360 : angle) / 45) % 8;

    // return relevant ascii arrow
    return ascii[index];
}

function init() {
    height = 1;
    width = 1;
    angle = 0
    cursor = rotation_ascii(angle)

    world = new Item('', { x: 0, y: 0 });

    robot = new Item('X', {x: 0, y: 0});

    myCanvas.append(world);

    myCanvas.append(robot);

    box = new Item(cursor, { x: 0, y: 0 });

    myCanvas.append(box);

    render();

    console.log('Requesting map from robot');
    socket.emit('json', JSON.stringify({
        'idKey': 'mapRequest',
    }));
}

// browser code
var pre = document.getElementById('myCanvas');
function render() {
    pre.innerHTML = myCanvas.toString();
}
window.addEventListener('keydown', function (e) {
    const { x, y } = box;

    switch (e.key) {
        case 'a':
            if (x > 1) {
                box.move({ x: x - 1 });
            }
            break;
        case 'd':
            if (x + width < COLS - 1) {
                box.move({ x: x + 1 });
            }
            break;
        case 'w':
            if (y - height > 0) {
                box.move({ y: y - 1 });
            }
            break;
        case 's':
            if (y + height < ROWS - 1) {
                box.move({ y: y + 1 });
            }
            break;
        case 'Enter':
            document.getElementById('destDecorator').innerText = 'Set dest to: ';
            document.getElementById('dest').innerText = box.x + ", " + box.y;
            document.getElementById('angleDecorator').innerText = 'Set angle to: ';
            document.getElementById('destAngle').innerText = angle;

            // send to socket
            socket.emit('json', JSON.stringify({
                'idKey': 'destUpdate',
                'dest': [box.x, box.y],
                'angle': angle
            }))

            setTimeout(() => {
                document.getElementById('destDecorator').innerText = 'Coords: ';
                document.getElementById('angleDecorator').innerText = 'Angle: ';
            }, 1000);
            break;
        case 'q':
            angle -= 5;
            if (angle < 0) {
                angle += 360; // wrap around
            }
            document.getElementById('angle').innerText = angle;
            cursor = rotation_ascii(angle);
            box.update(cursor);
            break;
        case 'e':
            angle += 5;
            if (angle >= 360) {
                angle -= 360; // wrap around
            }
            document.getElementById('angle').innerText = angle;
            cursor = rotation_ascii(angle);
            box.update(cursor);
            break;
    }

    document.getElementById('coords').innerText = box.x + ", " + box.y;

    render();
});