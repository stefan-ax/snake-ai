const board_border = 'black';
const board_background = "white";
const board_strips = '#c5decc';
const snake_col = 'lightblue';
const food_col = "red"
const snake_border = 'darkblue';

// TODO infer from API
const VIRTUAL_WIDTH = 32 // These are the dimension of the logical game.
const VIRTUAL_HEIGHT = 32// Take care that VIRTUAL_WIDTH * GAME_RATIO > GAME_WIDTH + GAME_RATIO
const GAME_RATIO = 10
const GAME_LATENCY = 90
const VELOCITY = 1
const KEYMAP = {37:"left", 39:"right", 38:"up", 40:"down"}

const snakeboard = document.getElementById("game");
const snakeboard_ctx = snakeboard.getContext("2d");

// WARNING set them according to VIRTUAL dimensions
GAME_WIDTH = snakeboard.width
GAME_HEIGHT = snakeboard.height

function main() {
    clearCanvas();

    let snake = new Snake();
    snake.drawSnake();
    snake.moveAuto();

    document.addEventListener("keydown", (event) => {
        snake.keyAct(event);
    });
}


function clearCanvas() {
    snakeboard_ctx.fillStyle = board_background;
    snakeboard_ctx.strokestyle = board_border;
    snakeboard_ctx.fillRect(0, 0, snakeboard.width, snakeboard.height);
    snakeboard_ctx.strokeRect(0, 0, snakeboard.width, snakeboard.height);

    for (let x = 0; x<=VIRTUAL_WIDTH; x++){
        for(let y = 0; y<=VIRTUAL_HEIGHT; y++)
            if ((x+y)%2==0){
                snakeboard_ctx.fillStyle = board_strips;
                snakeboard_ctx.fillRect(x*GAME_RATIO, y*GAME_RATIO, GAME_RATIO, GAME_RATIO);
            }

    }
}


class Snake {
    constructor(body=[{x:12, y:10}, {x:11, y:10}, {x: 10, y:10}]) {
        this.body = body;
        this.direction = null;
        this.current_food = new Food();
        this.interval = null;
    }

    drawSnake() {
        this.body.forEach(this.drawSnakePart);
    }

    drawSnakePart(snakePart) {
        snakeboard_ctx.fillStyle = snake_col;
        snakeboard_ctx.strokestyle = snake_border;

        snakeboard_ctx.fillRect(snakePart.x*GAME_RATIO, snakePart.y*GAME_RATIO, GAME_RATIO, GAME_RATIO);
        snakeboard_ctx.strokeRect(snakePart.x*GAME_RATIO, snakePart.y*GAME_RATIO, GAME_RATIO, GAME_RATIO);
    }

    move() {
        const direction = this.direction;

        if (direction == null)
            return;

        let new_head = {x:this.body[0].x, y:this.body[0].y}; // value of the old head here

        switch (direction) {
            case "right":
                new_head.x += VELOCITY;
                break;

            case "left":
                new_head.x -= VELOCITY;
                break;

            case "up":
                new_head.y -= VELOCITY;
                break;

            case "down":
                new_head.y += VELOCITY;
                break;
        }


        // Check if eaten food and make a new Food if necessary
        if (this.hasEatenFood(new_head.x, new_head.y)){
            console.log("eaten");
            this.current_food.initPosition();
            // do not remove old head
        }
        else
            this.body.pop(); // remove the old head

        this.body.unshift(new_head); // add the new head
        this.direction = direction;

        // Check if out of borders or self intersected
        if (this.isOut(new_head.x, new_head.y) || this.isIntersected(new_head.x, new_head.y))
        {
            this.moveStop()
            console.log("You lost!")
        }

        // Clear canvas and re-draw
        clearCanvas();
        this.drawSnake();
        this.current_food.drawFood();
    }

    moveAuto() {
        this.interval = setInterval(() => {this.move();}, GAME_LATENCY);
    }

    moveStop() {
        clearInterval(this.interval);
    }

    keyAct(event) {
         // Direction change
        const keyCode = event.keyCode;
        const directions = [KEYMAP[keyCode], this.direction];

        if (keyCode in KEYMAP) {
            // Check if not going in a forbidden direction
            if ((directions.includes("up") && directions.includes("down")) ||
                (directions.includes("left") && directions.includes("right")))
                return;
            else{
                this.direction = KEYMAP[keyCode];
                // setTimeout(function () {console.log("waiting")}, 100)
            }
        }

    }


    hasEatenFood(x, y) {
        return this.current_food.x == x && this.current_food.y == y;
    }

    isOut(x, y) {
        return (x>VIRTUAL_WIDTH) || (y>VIRTUAL_HEIGHT) || (x < 0) || (y < 0);
    }

    isIntersected(x, y) {
        for (let i = 1; i < this.body.length; i++) {
            if ((this.body[i].x == x) && (this.body[i].y == y))
                return true;
        }
        return false;
    }
}

class Food {
    constructor(x = null, y = null) {
        if (x == null || y == null){
            this.initPosition();
        }
    }

    initPosition() {
        this.x = Math.round((Math.random()*VIRTUAL_WIDTH));
        this.y = Math.round((Math.random()*VIRTUAL_HEIGHT));
    }

    drawFood() {
        snakeboard_ctx.fillStyle = food_col;
        snakeboard_ctx.strokeStyle = snake_border;
        snakeboard_ctx.fillRect(this.x*GAME_RATIO, this.y*GAME_RATIO, GAME_RATIO, GAME_RATIO);
        snakeboard_ctx.strokeRect(this.x*GAME_RATIO, this.y*GAME_RATIO, GAME_RATIO, GAME_RATIO);
    }

    isInterstected() {

    }


}
