/*

- setBoard() places pieces in starting positions
- square on mouse down turns cursor (css) into whatever piece is on the square
- square on release puts piece on that square if that move is legal
- if piece is taken (or pawn reaches end), piece on square is replaced and image = square's current piece

*/

function setBoard(board) {
    for(let row = 0; row < 8; row++)
        for(let col = 0; col < 8; col++)
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
    console.log("setting board");
    draw();
}

function draw() {
    for(let row = 0; row < 8; row++)
        for(let col = 0; col < 8; col++)
            if(board[row][col]) placePiece(document.getElementById(`${row},${col}`), board[row][col]);
}

function pickUpPiece(square) {
    console.log("Picked up piece from " + square.id);
}

function placePiece(square, piece) {
    console.log("Placed piece on " + square.id);
    square.style.backgroundImage = `url(static/images/pieces/${piece}.png)`;
    square.style.backgroundRepeat = "no-repeat";
    square.style.backgroundPosition = "center";
    square.style.backgroundSize = "cover";
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

const whiteStart = [
    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'
];

document.onload = setBoard(board);