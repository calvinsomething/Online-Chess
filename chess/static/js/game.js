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
    console.log(data);
};

function legalMoves(data) {
    moves = data['moves'];

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
                document.getElementById(`${row},${col}`).style.backgroundColor = highlight;
            }
        }
    }
}

function clearHighlights() {
    for (let row = 0; row < 8; row++)
        for (let col = 0; col < 8; col++) {
            document.getElementById(`${row},${col}`).style.backgroundColor = null;
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
    fetch(findGameUrl, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': token
        },
        body: JSON.stringify({
            'opponent': opponent
        })
    },)
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function newGame(opponent) {
    fetch(newGameUrl, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': token
        },
        body: JSON.stringify({
            'opponent': opponent
        })
    },)
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
      });
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
const boardUrl = 0;
function getBoard() {
    fetch(boardUrl, {credentials: 'include'})
    .then(rsp => rsp.json())
    .then(data => {
        console.log("Data:", data)
    })
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
        draw();
        return;
    }
    for (let row = 0; row < 8; row++)
        for (let col = 0; col < 8; col++) {
            const sq = row * 8 + col % 8;
            board[row][col] = translate(official[sq]);
        }
    playerColor = 'W';
    draw();
}

function draw() {
    for (let row = 0; row < 8; row++)
        for (let col = 0; col < 8; col++) {
            const square = document.getElementById(`${row},${col}`);
            const piece = board[row][col];
            if (piece) {
                square.style.backgroundImage = `url(static/images/pieces/${piece}.png)`;
                square.style.backgroundRepeat = "no-repeat";
                square.style.backgroundPosition = "center";
                square.style.backgroundSize = "cover";
            }
            else
                square.style.backgroundImage = null;
        }
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
        if(width > 1200)
            document.getElementById("board").style.cursor = `url(static/images/pieces/${inHand}.png) 60 60, default`;
        else if(width > 992)
            document.getElementById("board").style.cursor = `url(static/images/pieces/Medium/${inHand}.png) 45 45, default`;
        else
            document.getElementById("board").style.cursor = `url(static/images/pieces/Small/${inHand}.png) 30 30, default`;

    console.log("Picked up piece from " + square.id);
}

function getSquare(squareId) {
    var square = parseInt(squareId[0]) * 8 + parseInt(squareId[2]);
    if (playerColor === 'B') square = 63 - square;
    return square;
}

function placePiece(e) {
    if (!inHand) return;
    document.getElementById("board").style.cursor = "default";
    var square = e.target;
    console.log("Placed piece on " + square.id);
    if (square.style.backgroundColor === highlight) {
        socket.send(JSON.stringify({
            'makeMove': [getSquare(takenFrom), getSquare(square.id)]
        }));
    }

    if(inHand) {
        board[square.id[0]][square.id[2]] = inHand;
        inHand = '';
        clearHighlights();
    }
}

function getWinSize() {
    

    var height = window.innerHeight
    || document.documentElement.clientHeight
    || document.body.clientHeight;
    return [width, height];
}

function Square() {

}


let board = [];
for(let row = 0; row < 8; row++)
    board[row] = [];
let playerColor;
let takenFrom;
let inHand;
let myTurn = false;

// const whiteStart = [
//     'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'
// ];

//document.onload = setBoard();
//newGame();
//getBoard();