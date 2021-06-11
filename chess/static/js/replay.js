function translate(piece) {
    if (piece === '0') return 0;
    if (piece === piece.toLowerCase())
        return `W${piece.toUpperCase()}`;
    else return `B${piece}`;
}

function draw(row, col, piece) {
    console.log('drawing piece ' + piece + '...');
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

function setBoard() {
    console.log("setting board...")
    for (let row = 0; row < 8; row++)
        for (let col = 0; col < 8; col++) {
            const piece = translate(board[row][col]);
            draw(row, col, piece);
        }
}

function move(from, to, fwdIndex) {
    var row = Math.floor(parseInt(from) / 8);
    var col = parseInt(from) % 8;
    const piece = board[row][col];
    if (lastCap && movesIndex === lastCap.index)
    {
        board[row][col] = captured[--capIndex];
        lastCap = lastCap.prev;
    }
    else
        board[row][col] = '0';
    draw(row, col, translate(board[row][col]));
    row = Math.floor(parseInt(to) / 8);
    col = parseInt(to) % 8;
    if (board[row][col] !== '0')
    {
        lastCap = CapNode(fwdIndex, lastCap);
        capIndex++;
    }
    board[row][col] = piece;
    draw(row, col, translate(piece));
}

function forward() {
    if (movesIndex == moveHistory.length)
            return;
    const start = movesIndex;
    var from = '', to = '';
    while (moveHistory[movesIndex] !== ',')
        from += moveHistory[movesIndex++]; 
    movesIndex++;
    while (moveHistory[movesIndex] !== ';')
        to += moveHistory[movesIndex++];
    movesIndex++;
    move(from, to, start);
}

function back() {
    if (movesIndex == 0)
            return;
    movesIndex -= 2;
    while (moveHistory[--movesIndex] !== ';' && movesIndex > -1) {}
    movesIndex++;
    var tempIndex = movesIndex;
    var from = '', to = '';
    while (moveHistory[tempIndex] !== ',')
        to += moveHistory[tempIndex++];
    tempIndex++;
    while (moveHistory[tempIndex] !== ';')
        from += moveHistory[tempIndex++];
    move(from, to, 0);
}

function CapNode(index, prev) {
    return {
        'index': index,
        'prev': prev,
        'next': null,
        'init': () => {this.prev.next = this;}
    }
}


// function setBoard() {
//     if (playingBlack) {
//         var sq = 64;
//         for (let row = 0; row < 8; row++)
//             for (let col = 0; col < 8; col++) {
//                 sq -= 1;
//                 board[row][col] = translate(official[sq]);
//         }
//         playerColor = 'B';
//     } else {
//     for (let row = 0; row < 8; row++)
//         for (let col = 0; col < 8; col++) {
//             const sq = row * 8 + col % 8;
//             board[row][col] = translate(official[sq]);
//         }
//     playerColor = 'W';
//     }
//     draw();
//     sound.play();
//     if (data['captured']){
//         drawCaptured(data['captured']);
//     }
// }


// function updateBoard(data) {
//     official = data['board'];
//     const winner = data['winner'];
//     if (winner) {
//         var msg;
//         switch (winner) {
//             case 'W':
//                 var msg = "Game Over. White wins.";
//                 break
//             case 'B':
//                 var msg = "Game Over. Black wins.";
//                 break
//             case 'D':
//                 var msg = "Game Over. Draw.";
//         }
//         window.alert(msg);
//     }
//     if (data['myTurn'] === 'True') myTurn = true;
//     else myTurn = false;
//     if (data['playingBlack']) {
//         var sq = 64;
//         for (let row = 0; row < 8; row++)
//             for (let col = 0; col < 8; col++) {
//                 sq -= 1;
//                 board[row][col] = translate(official[sq]);
//         }
//         playerColor = 'B';
//     } else {
//     for (let row = 0; row < 8; row++)
//         for (let col = 0; col < 8; col++) {
//             const sq = row * 8 + col % 8;
//             board[row][col] = translate(official[sq]);
//         }
//     playerColor = 'W';
//     }
//     draw();
//     sound.play();
//     if (data['captured']){
//         drawCaptured(data['captured']);
//     }
// }

// function newCapturedImg(img, side, bottom) {
//     const newColS = document.createElement('div');
//     newColS.className = 'col-1 pl-xl-4';
//     newColS.style= 'width: 30px;';
//     const newImgS = document.createElement('img');
//     newImgS.src = img;
//     newImgS.style = sideStyle;
//     newColS.appendChild(newImgS);
//     const newColB = document.createElement('div');
//     newColB.className = 'col-1';
//     const newImgB = document.createElement('img');
//     newImgB.src = img;
//     newImgB.style = bottomStyle;
//     newColB.appendChild(newImgB);
//     side.appendChild(newColS);
//     bottom.appendChild(newColB);
// }

// function drawCaptured(captured) {
//     const sections = [
//         myPawnsS, myPiecesS, ePawnsS, ePiecesS, myPawnsB, myPiecesB, ePawnsB, ePiecesB
//     ];
//     for (section of sections)
//         section.innerHTML = '';
//     const order = ['Q', 'B', 'N', 'R', 'q', 'b', 'n', 'r']
//     const bPawns = captured.match(/P/g);
//     const wPawns = captured.match(/p/g);
//     if (bPawns)
//         for (i = 0; i < bPawns.length; i++)
//             if (playerColor === 'B')
//                 newCapturedImg(bPawnImg, myPawnsS, myPawnsB);
//             else
//                 newCapturedImg(bPawnImg, ePawnsS, ePawnsB);
//     if (wPawns)
//         for (i = 0; i < wPawns.length; i++)
//             if (playerColor === 'B') 
//                 newCapturedImg(wPawnImg, ePawnsS, ePawnsB);
//             else 
//                 newCapturedImg(wPawnImg, myPawnsS, myPawnsB);
//     var bPieces = captured.split('').filter((piece) => (piece !== 'P' && piece !== piece.toLowerCase()));
//     var wPieces = captured.split('').filter((piece) => (piece !== 'p' && piece !== piece.toUpperCase()));
//     if (bPieces)
//         bPieces.sort((a, b) => order.findIndex(ele => ele === a) - order.findIndex(ele => ele === b));
//         for (piece of bPieces) {
//             var img;
//             switch (piece) {
//                 case 'Q':
//                     img = bQueenImg;
//                     break;
//                 case 'B':
//                     img = bBishopImg;
//                     break;
//                 case 'N':
//                     img = bKnightImg;
//                     break;
//                 case 'R':
//                     img = bRookImg;
//             }
//             if (playerColor === 'B') 
//                 newCapturedImg(img, myPiecesS, myPiecesB);
//             else 
//                 newCapturedImg(img, ePiecesS, ePiecesB);
//         }
//     if (wPieces)
//         console.log(wPieces);
//         wPieces.sort((a, b) => order.findIndex(ele => ele === a) - order.findIndex(ele => ele === b));
//         for (piece of wPieces) {
//             var img;
//             switch (piece) {
//                 case 'q':
//                     img = wQueenImg;
//                     break;
//                 case 'b':
//                     img = wBishopImg;
//                     break;
//                 case 'n':
//                     img = wKnightImg;
//                     break;
//                 case 'r':
//                     img = wRookImg;
//             }
//             if (playerColor === 'B') 
//                 newCapturedImg(img, ePiecesS, ePiecesB);
//             else 
//                 newCapturedImg(img, myPiecesS, myPiecesB);
//         }
// }

// function draw() {
//     for (let row = 0; row < 8; row++)
//         for (let col = 0; col < 8; col++) {
//             const square = document.getElementById(`${row},${col}`);
//             const piece = board[row][col];
//             if (piece) {
//                 square.style.backgroundImage = `url(${imgDir}${piece}.png)`;
//                 square.style.backgroundRepeat = "no-repeat";
//                 square.style.backgroundPosition = "center";
//                 square.style.backgroundSize = "cover";
//             }
//             else
//                 square.style.backgroundImage = null;
//         }
//     clearHighlights();
// }


// function getSquare(squareId) {
//     var square = parseInt(squareId[0]) * 8 + parseInt(squareId[2]);
//     if (playerColor === 'B') square = 63 - square;
//     return square;
// }

// function placePiece(e) {
//     if (!inHand) return;
//     const square = e.target;
//     console.log("Placed piece on " + square.id);
//     console.log(square.classList);
//     if (square.classList.contains("legal")) {
//         socket.send(JSON.stringify({
//             'makeMove': [getSquare(takenFrom), getSquare(square.id)]
//         }));
//     } else {
//         board[parseInt(takenFrom[0])][parseInt(takenFrom[1])] = inHand;
//         draw();
//     }
//     document.getElementById("board").style.cursor = "default";
//     inHand = '';
// }

// function getWinSize() {
//     var height = window.innerHeight
//         || document.documentElement.clientHeight
//         || document.body.clientHeight;
//     return [width, height];
// }


let lastCap, movesIndex = 0, promoIndex = 0, capIndex = 0;
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
const fwd = document.getElementsByClassName('next');
for (button of fwd)
    button.addEventListener('click', forward);
const prev = document.getElementsByClassName('prev');
for (button of prev)
    button.addEventListener('click', back);
console.log(moveHistory);