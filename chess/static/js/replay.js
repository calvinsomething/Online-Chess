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
}

function move(from, to, fwd = true) {
    var row = Math.floor(parseInt(from) / 8);
    var col = parseInt(from) % 8;
    const piece = board[row][col];
    //if piece = k && checkCastle()
    //  castle code
    if (!fwd && moveCount === nextEnPassant[epi - 1]) {
        reverseEP(row, col);
        board[row][col] = '0';
    } else if (!fwd && moveCount === lastCap[capIndex - 1])
        board[row][col] = captured[--capIndex];
    else
        board[row][col] = '0';
    draw(row, col);
    row = Math.floor(parseInt(to) / 8);
    col = parseInt(to) % 8;
    if (fwd && moveCount === nextEnPassant[epi])
        enPassant(row, col);
    else if (board[row][col] !== '0')
        lastCap[capIndex++] = moveCount;
    board[row][col] = piece;
    draw(row, col);
}

function forward() {
    if (movesIndex == movesList.length)
            return;
    const start = movesIndex;
    move(movesList[movesIndex++], movesList[movesIndex++]);
    moveCount++;
}

function back() {
    if (movesIndex == 0)
            return;
    moveCount--;
    move(movesList[--movesIndex], movesList[--movesIndex], false);
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


let movesIndex = 0, promoIndex = 0, capIndex = 0, epi = 0, moveCount = 0;
let nextEnPassant = [], lastCap = [];
for (let i = 0; i < captured.length; i++)
    lastCap.push(0);
let temp = '';
for (let x of ePIndex) {
    if (x === ',') {
        nextEnPassant.push(parseInt(temp));
        temp = '';
    } else {
        temp += x;
    }
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