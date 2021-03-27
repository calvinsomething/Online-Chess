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
    if (playerColor === 'B') {
        var sq = 64;
        for (let row = 0; row < 8; row++)
            for (let col = 0; col < 8; col++) {
                sq -= 1;
                if(moves[sq] === '1')
                    document.getElementById(`${row},${col}`).style.backgroundColor = highlight;
        }
        return;
    }
    for (let row = 0; row < 8; row++)
        for (let col = 0; col < 8; col++) {
            const sq = row * 8 + col % 8;
            if(moves[sq] === '1')
                    document.getElementById(`${row},${col}`).style.backgroundColor = highlight;
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

// function setBoard() {
//     takenFrom = undefined;
//     for(let row = 0; row < 8; row++)
//         for(let col = 0; col < 8; col++) {
//             switch(row) {
//                 case 0:
//                     board[row][col] = 'B' + whiteStart[col];
//                     break;
//                 case 7:
//                     board[row][col] = 'W' + whiteStart[col];
//                     break;
//                 case 1:
//                     board[row][col] = 'BP';
//                     break;
//                 case 6:
//                     board[row][col] = 'WP';
//             }
//             draw(document.getElementById(`${row},${col}`), board[row][col]);
//         }
//     console.log("setting board");
// }

function getLegalMoves(squareId) {
    var square = parseInt(squareId[0]) * 8 + parseInt(squareId[2]) % 8;
    if (playerColor === 'B') square = 63 - square;
    socket.send(JSON.stringify({
        'getMoves': square
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

function placePiece(e) {
    var square = e.target
    console.log("Placed piece on " + square.id);
    // if move is legal
    // modify board
    // then modify display
    if(takenFrom) {
        board[takenFrom[0]][takenFrom[2]] = '';
        //draw(document.getElementById(takenFrom), '');
    }
    if(inHand) {
        board[square.id[0]][square.id[2]] = inHand;
        //draw(square, inHand);
        inHand = '';
        clearHighlights();
    }
    
    document.getElementById("board").style.cursor = "default";

    // socket.send(JSON.stringify({
    //     'board': square.id
    // }));
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