function translate(piece) {
    if (piece === '0') return 0;
    if (piece === piece.toLowerCase())
        return `W${piece.toUpperCase()}`;
    else return `B${piece}`;
}

function draw(row, col) {
    const piece = translate(board[row][col]);
    if (playingBlack) {
        row = 7 - row;
        col = 7 - col;
    }
    const square = document.getElementById(`${row},${col}`);
    if (piece) {
        square.style.backgroundImage = `url(${imgDir}${piece}.png)`;
        square.style.backgroundRepeat = "no-repeat";
        square.style.backgroundPosition = "center";
        square.style.backgroundSize = "cover";
    } else {
        square.style.backgroundImage = null;
    }
}

function makeMovesList(moves) {
    var i = 0, newList = [];
    while (i < moves.length) {
        var from = '', to = '';
        while (moves[i] !== ',')
            from += moves[i++];
        i++;
        while (moves[i] !== ';')
            to += moves[i++];
        i++;
        newList.push(parseInt(from));
        newList.push(parseInt(to));
    }
    return newList;
}

function setBoard() {
    console.log("setting board...")
    for (let row = 0; row < 8; row++)
        for (let col = 0; col < 8; col++)
            draw(row, col);      
}

function enPassant(row, col) {
    if (row === 2) {
        board[++row][col] = '0';
        draw(row, col);
    } else {
        board[--row][col] = '0';
        draw(row, col);
    }
    console.log("Capturing with en Passant...");
    console.log(nextEnPassant[epi]);
    console.log(captured);
    console.log(capIndex);
    epi++;
    capIndex++;
}

function reverseEP(row, col) {
    if (row === 2) {
        board[++row][col] = 'P';
        draw(row, col);
    } else {
        board[--row][col] = 'p';
        draw(row, col);
    }
    epi--;
    capIndex--;
    console.log("Capturing with en Passant...");
    console.log(nextEnPassant[epi]);
    console.log(captured);
    console.log(capIndex);
}

function castle(row, col) {
    var to, from;
    if (col === 2) {
        from = 0;
        to = 3;
    } else {
        from = 7;
        to = 5;
    }
    board[row][to] = board[row][from];
    board[row][from] = '0';
    draw(row, from);
    draw(row, to);
}

function revCastle(row, col) {
    var to, from;
    if (col === 2) {
        from = 3;
        to = 0;
    } else {
        from = 5;
        to = 7;
    }
    board[row][to] = board[row][from];
    board[row][from] = '0';
    draw(row, from);
    draw(row, to);
}

function move(from, to, fwd = true) {
    var row = Math.floor(parseInt(from) / 8);
    var col = parseInt(from) % 8;
    var piece = board[row][col];
    if (!fwd && moveCount === nextEnPassant[epi - 1])
        reverseEP(row, col);
    else if (!fwd && piece.toLowerCase() === 'k' && Math.abs(to - from) > 1)
        revCastle(row, col);
    else if (!fwd && moveCount === promoMoves[promoIndex - 1]) {
        piece = row == 0 ? 'p' : 'P';
        promoIndex--;
    }
    if (!fwd && moveCount === lastCap[capIndex - 1]) {
        console.log(`Reversing capture of ${captured[capIndex - 1]}`);
        console.log(captured);
        console.log(capIndex);
        board[row][col] = captured[--capIndex];
    }
    else 
        board[row][col] = '0';
    draw(row, col);
    row = Math.floor(parseInt(to) / 8);
    col = parseInt(to) % 8;
    if (fwd) {
        if (moveCount === nextEnPassant[epi])
            enPassant(row, col);
        else if (board[row][col] !== '0') {
            console.log("Capturing...");
            console.log(captured);
            console.log(capIndex);
            lastCap[capIndex++] = moveCount;
        }
        else if (piece.toLowerCase() === 'k' && Math.abs(to - from) > 1)
            castle(row, col);
    }
    if (fwd && piece.toLowerCase() === 'p' && (row === 0 || row === 7)) {
        piece = promotions[promoIndex];
        promoMoves[promoIndex++] = moveCount;
    }
    board[row][col] = piece;
    draw(row, col);
}

function forward() {
    if (movesIndex == movesList.length)
            return;
    console.log('Moving forward...');
    console.log(moveCount);
    console.log(nextEnPassant[epi]);
    const start = movesIndex;
    move(movesList[movesIndex++], movesList[movesIndex++]);
    moveCount++;
    sound.play();
}

function back() {
    if (movesIndex == 0)
            return;
    moveCount--;
    move(movesList[--movesIndex], movesList[--movesIndex], false);
    console.log('Moving backward...');
    console.log(moveCount);
    console.log(nextEnPassant[epi]);
}


let movesIndex = 0, promoIndex = 0, promoMoves = Array(promotions.length), capIndex = 0, epi = 0, moveCount = 0;
let nextEnPassant = [], lastCap = Array(captured.length);
for (let i = 0; i < captured.length; i++)
    lastCap[i] = 0;
let temp = '';
for (let i = 0; i < ePIndex.length; i++) {
    if (ePIndex[i] === ',') {
        nextEnPassant.push(parseInt(temp));
        temp = '';
    } else
        temp += ePIndex[i];
}
const sound = document.getElementById('sound');
const myPawnsS = document.getElementById("my-pawns-s");
const myPiecesS = document.getElementById("my-pieces-s");
const ePawnsS = document.getElementById("e-pawns-s");
const ePiecesS = document.getElementById("e-pieces-s");
const myPawnsB = document.getElementById("my-pawns-b");
const myPiecesB = document.getElementById("my-pieces-b");
const ePawnsB = document.getElementById("e-pawns-b");
const ePiecesB = document.getElementById("e-pieces-b");
sideStyle = "object-position: 0px 0px; width: 100px;";
bottomStyle = "object-position: -10px 0px; width: 70px;";
const bPawnImg = `${imgDir}BP.png`;
const wPawnImg = `${imgDir}WP.png`;
const bRookImg = `${imgDir}BR.png`;
const wRookImg = `${imgDir}WR.png`;
const bKnightImg = `${imgDir}BN.png`;
const wKnightImg = `${imgDir}WN.png`;
const bBishopImg = `${imgDir}BB.png`;
const wBishopImg = `${imgDir}WB.png`;
const bQueenImg = `${imgDir}BQ.png`;
const wQueenImg = `${imgDir}WQ.png`;
let board = [
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['0', '0', '0', '0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0', '0', '0', '0'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
]

setBoard();
const movesList = makeMovesList(moveHistory);

const fwd = document.getElementsByClassName('next');
for (button of fwd)
    button.addEventListener('click', forward);
const prev = document.getElementsByClassName('prev');
for (button of prev)
    button.addEventListener('click', back);
console.log(moveHistory);
console.log(`Playing Black: ${playingBlack}, winner: ${winner}, count: ${count}, en passants: ${ePIndex}, promotions: ${promotions}`);
console.log(promoMoves);
console.log(lastCap);