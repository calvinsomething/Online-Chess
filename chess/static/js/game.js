const token = getCookie('csrftoken');
const highlight = 'rgb(74, 171, 216)';

const socket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/user/'
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data['challenger']) challenges(data);
    if (data['board']) updateBoard(data);
    if (data['moves']) legalMoves(data);
    if (data['promote']) promote(data);
    console.log(data);
};

function legalMoves(data) {
    const moves = data['moves'];
    for (let half = 0; half < 2; half++) {
        console.log(moves[half]);
        if (moves[half] === 0) continue;
        for (let sq = 0; sq < 32; sq++) {
            if (moves[half] & 1 << (31 - sq)) {
                console.log(sq);
                var row = Math.floor(sq / 8) + half * 4;
                var col = sq % 8;
                if (playerColor === 'B') {
                    row = 7 - row;
                    col = 7 - col;
                }
                const square = document.getElementById(`${row},${col}`);
                square.classList.add('legal');
                square.style.backgroundColor = highlight;
            }
        }
    }
}

//Temporary until I can build in the promotion options into the side pannel
function promote(data) {
    var promotion = '0';
    while (!(promotion.toUpperCase() === 'Q' || promotion.toUpperCase() === 'B'
        || promotion.toUpperCase() === 'N' || promotion.toUpperCase() === 'R'))
        promotion = window.prompt("Enter 'Q', 'B', 'N', or 'R' to choose your promotion.", "Enter Letter: ");
    socket.send(JSON.stringify({
        'promotion': promotion
    }));
}

function clearHighlights() {
    const elements = document.getElementsByClassName('legal');
    while (elements.length) {
        elements[0].style.backgroundColor = null;
        elements[0].classList.remove('legal');
    }
}

function challenges(data) {
    acceptChallenge = window.confirm(`Challenge incoming from ${data['challenger']}. Do you accept?`);
    if (acceptChallenge)
        newGame(data['challenger']);
}

socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};

document.getElementById("findGame").addEventListener('click', findGame);

['sq-w', 'sq-b'].forEach(sq => {
    for (element of document.getElementsByClassName(sq)) {
        element.addEventListener('mousedown', pickUpPiece);
        element.addEventListener('mouseup', placePiece);
    }
});


function findGame() {
    var opponent = window.prompt("Enter opponent's username: ", "Username");
    // fetch(findGameUrl, {
    //     method: 'POST',
    //     credentials: 'include',
    //     headers: {
    //         'Content-Type': 'application/json',
    //         'X-CSRFToken': token
    //     },
    //     body: JSON.stringify({
    //         'opponent': opponent
    //     })
    // },)
    // .then(response => response.json())
    // .then(data => {
    //     console.log('Success:', data);
    // })
    // .catch((error) => {
    //     console.error('Error:', error);
    // });
    socket.send(JSON.stringify({
        'challenge': opponent
    }));
}

function newGame(opponent) {
    // fetch(newGameUrl, {
    //     method: 'POST',
    //     credentials: 'include',
    //     headers: {
    //         'Content-Type': 'application/json',
    //         'X-CSRFToken': token
    //     },
    //     body: JSON.stringify({
    //         'opponent': opponent
    //     })
    // },)
    // .then(response => response.json())
    // .then(data => {
    //     console.log('Success:', data);
    // })
    // .catch((error) => {
    //     console.error('Error:', error);
    //   });
    socket.send(JSON.stringify({
        'gameVS': opponent
    }));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getLegalMoves(squareId) {
    socket.send(JSON.stringify({
        'getMoves': getSquare(squareId) + 1
    }));
}

function translate(piece) {
    if (piece === '0') return 0;
    if (piece === piece.toLowerCase())
        return `W${piece.toUpperCase()}`;
    else return `B${piece}`;
}

function updateBoard(data) {
    official = data['board'];
    const winner = data['winner'];
    if (winner) {
        var msg;
        switch (winner) {
            case 'W':
                var msg = "Game Over. White wins.";
                break
            case 'B':
                var msg = "Game Over. Black wins.";
                break
            case 'D':
                var msg = "Game Over. Draw.";
        }
        window.alert(msg);
    }
    if (data['myTurn'] === 'True') myTurn = true;
    else myTurn = false;
    if (data['playingBlack']) {
        var sq = 64;
        for (let row = 0; row < 8; row++)
            for (let col = 0; col < 8; col++) {
                sq -= 1;
                board[row][col] = translate(official[sq]);
        }
        playerColor = 'B';
    } else {
    for (let row = 0; row < 8; row++)
        for (let col = 0; col < 8; col++) {
            const sq = row * 8 + col % 8;
            board[row][col] = translate(official[sq]);
        }
    playerColor = 'W';
    }
    draw();
    sound.play();
    if (data['captured']){
        drawCaptured(data['captured']);
    }
}

function newCapturedImg(img, side, bottom) {
    const newColS = document.createElement('div');
    newColS.className = 'col-1 pl-xl-4';
    newColS.style= 'width: 30px;';
    const newImgS = document.createElement('img');
    newImgS.src = img;
    newImgS.style = sideStyle;
    newColS.appendChild(newImgS);
    const newColB = document.createElement('div');
    newColB.className = 'col-1';
    const newImgB = document.createElement('img');
    newImgB.src = img;
    newImgB.style = bottomStyle;
    newColB.appendChild(newImgB);
    side.appendChild(newColS);
    bottom.appendChild(newColB);
}

function drawCaptured(captured) {
    const sections = [
        myPawnsS, myPiecesS, ePawnsS, ePiecesS, myPawnsB, myPiecesB, ePawnsB, ePiecesB
    ];
    for (section of sections)
        section.innerHTML = '';
    const order = ['Q', 'B', 'N', 'R', 'q', 'b', 'n', 'r']
    const bPawns = captured.match(/P/g);
    const wPawns = captured.match(/p/g);
    if (bPawns)
        for (i = 0; i < bPawns.length; i++)
            if (playerColor === 'B')
                newCapturedImg(bPawnImg, myPawnsS, myPawnsB);
            else
                newCapturedImg(bPawnImg, ePawnsS, ePawnsB);
    if (wPawns)
        for (i = 0; i < wPawns.length; i++)
            if (playerColor === 'B') 
                newCapturedImg(wPawnImg, ePawnsS, ePawnsB);
            else 
                newCapturedImg(wPawnImg, myPawnsS, myPawnsB);
    var bPieces = captured.split('').filter((piece) => (piece !== 'P' && piece !== piece.toLowerCase()));
    var wPieces = captured.split('').filter((piece) => (piece !== 'p' && piece !== piece.toUpperCase()));
    if (bPieces)
        bPieces.sort((a, b) => order.findIndex(ele => ele === a) - order.findIndex(ele => ele === b));
        for (piece of bPieces) {
            var img;
            switch (piece) {
                case 'Q':
                    img = bQueenImg;
                    break;
                case 'B':
                    img = bBishopImg;
                    break;
                case 'N':
                    img = bKnightImg;
                    break;
                case 'R':
                    img = bRookImg;
            }
            if (playerColor === 'B') 
                newCapturedImg(img, myPiecesS, myPiecesB);
            else 
                newCapturedImg(img, ePiecesS, ePiecesB);
        }
    if (wPieces)
        console.log(wPieces);
        wPieces.sort((a, b) => order.findIndex(ele => ele === a) - order.findIndex(ele => ele === b));
        for (piece of wPieces) {
            var img;
            switch (piece) {
                case 'q':
                    img = wQueenImg;
                    break;
                case 'b':
                    img = wBishopImg;
                    break;
                case 'n':
                    img = wKnightImg;
                    break;
                case 'r':
                    img = wRookImg;
            }
            if (playerColor === 'B') 
                newCapturedImg(img, ePiecesS, ePiecesB);
            else 
                newCapturedImg(img, myPiecesS, myPiecesB);
        }
}

function draw() {
    for (let row = 0; row < 8; row++)
        for (let col = 0; col < 8; col++) {
            const square = document.getElementById(`${row},${col}`);
            const piece = board[row][col];
            if (piece) {
                square.style.backgroundImage = `url(${imgDir}${piece}.png)`;
                square.style.backgroundRepeat = "no-repeat";
                square.style.backgroundPosition = "center";
                square.style.backgroundSize = "cover";
            }
            else
                square.style.backgroundImage = null;
        }
    clearHighlights();
}

function pickUpPiece(e) {
    if (!myTurn) return;
    var square = e.target;
    if (board[square.id[0]][square.id[2]][0] !== playerColor)
        return;
    if(!inHand) {
        inHand = board[square.id[0]][square.id[2]];
        getLegalMoves(square.id);
        takenFrom = square.id;
        square.style.backgroundImage = null;
    }
    var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    if(inHand)
        if(width > 992)
            document.getElementById("board").style.cursor = `url(${imgDir}${inHand}.png) 60 60, default`;
        else if(width > 576)
            document.getElementById("board").style.cursor = `url(${imgDir}Medium/${inHand}.png) 45 45, default`;
        else
            document.getElementById("board").style.cursor = `url(${imgDir}Small/${inHand}.png) 30 30, default`;

    console.log("Picked up piece from " + square.id);
}

function getSquare(squareId) {
    var square = parseInt(squareId[0]) * 8 + parseInt(squareId[2]);
    if (playerColor === 'B') square = 63 - square;
    return square;
}

function placePiece(e) {
    if (!inHand) return;
    const square = e.target;
    console.log("Placed piece on " + square.id);
    console.log(square.classList);
    if (square.classList.contains("legal")) {
        socket.send(JSON.stringify({
            'makeMove': [getSquare(takenFrom), getSquare(square.id)]
        }));
    } else {
        board[parseInt(takenFrom[0])][parseInt(takenFrom[1])] = inHand;
        draw();
    }
    document.getElementById("board").style.cursor = "default";
    inHand = '';
}

function getWinSize() {
    var height = window.innerHeight
        || document.documentElement.clientHeight
        || document.body.clientHeight;
    return [width, height];
}

let board = [];
for(let row = 0; row < 8; row++)
    board[row] = [];
let playerColor;
let takenFrom;
let inHand;
let myTurn = false;
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