const token = getCookie('csrftoken');

const socket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/user/'
    // + '/ws/game/1/'
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data);
};

socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};

document.getElementById("findGame").addEventListener('click', findGame);

['sq-w', 'sq-b'].forEach(sq => {
    for(element of document.getElementsByClassName(sq)) {
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

function newGame() {
    fetch(newGameUrl, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': token
        }
    })
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

function getBoard() {
    fetch(boardUrl, {credentials: 'include'})
    .then(rsp => rsp.json())
    .then(data => {
        console.log("Data:", data)
    })
}

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
    if(piece) {
        square.style.backgroundImage = `url(static/images/pieces/${piece}.png)`;
        square.style.backgroundRepeat = "no-repeat";
        square.style.backgroundPosition = "center";
        square.style.backgroundSize = "cover";
    }
    else
        square.style.backgroundImage = null;
}

function pickUpPiece(e) {
    var square = e.target
    if(!inHand) {
        inHand = board[square.id[0]][square.id[2]];
        takenFrom = square.id;
        draw(square, '');
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
        draw(document.getElementById(takenFrom), '');
    }
    if(inHand) {
        board[square.id[0]][square.id[2]] = inHand;
        draw(square, inHand);
        inHand = '';
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
for(let row = 0; row < 8; row++) {
    board[row] = [];
    for(let col = 0; col < 8; col++) {
        board[row][col] = '';
    }
}

let takenFrom;
let inHand;

const whiteStart = [
    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'
];

document.onload = setBoard();
//newGame();
//getBoard();