/*

- setBoard() places pieces in starting positions
- square on mouse down turns cursor (css) into whatever piece is on the square
- square on release puts piece on that square if that move is legal
- if piece is taken (or pawn reaches end), piece on square is replaced and image = square's current piece

*/

function setBoard() {
    takenFrom = undefined;
    for(let row = 0; row < 8; row++)
        for(let col = 0; col < 8; col++) {
            switch(row) {
                case 0:
                    board[row][col] = 'B' + whiteStart[col];
                    break;
                case 7:
                    board[row][col] = 'W' + whiteStart[col];
                    break;
                case 1:
                    board[row][col] = 'BP';
                    break;
                case 6:
                    board[row][col] = 'WP';
            }
            draw(document.getElementById(`${row},${col}`), board[row][col]);
        }
    console.log("setting board");
}

function draw(square, piece) {
    if(piece !== '0') {
        square.style.backgroundImage = `url(static/images/pieces/${piece}.png)`;
        square.style.backgroundRepeat = "no-repeat";
        square.style.backgroundPosition = "center";
        square.style.backgroundSize = "cover";
    }
    else
        square.style.backgroundImage = null;
}

function pickUpPiece(square) {
    inHand = board[square.id[0]][square.id[2]];
    takenFrom = square.id;
    //change cursor icon in CSS
    console.log("Picked up piece from " + square.id);
}

function placePiece(square) {
    console.log("Placed piece on " + square.id);
    if(inHand !== '0') {
        board[square.id[0]][square.id[2]] = inHand;
        draw(square, inHand);
    }
    if(takenFrom) {
        board[takenFrom[0]][takenFrom[2]] = '0';
        draw(document.getElementById(takenFrom), '0');
    }
}

function Square() {

}


let board = [];
for(let row = 0; row < 8; row++) {
    board[row] = [];
    for(let col = 0; col < 8; col++) {
        board[row][col] = '0';
    }
}

let takenFrom;
let inHand;

const whiteStart = [
    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'
];

document.onload = setBoard();