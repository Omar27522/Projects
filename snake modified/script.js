// Define HTML elements
const board = document.getElementById('game-board');
const instructionText = document.getElementById('instruction-text');
const logo = document.getElementById('logo');
const score = document.getElementById('score');
const highScoreText = document.getElementById('highScore');

// Define game variables
const gridSize = 20;
let snake = [{ x: 10, y: 10 }];
let food = generateFood();
let highScore = 0;
let direction = 'right';
let gameInterval;
let gameSpeedDelay = 200;
let gameStarted = false;
let touchStartX = 0;
let touchStartY = 0;

// Draw game map, snake, food
function draw() {
  board.innerHTML = '';
  drawSnake();
  drawFood();
  updateScore();
}

// Draw snake
// Draw snake
function drawSnake() {
  snake.forEach((segment, index) => {
    const snakeElement = createGameElement('div', 'snake');
    if (index === 0) {
      snakeElement.id = 'firstSnake'; // Add a unique ID to the first element
    }
    setPosition(snakeElement, segment);
    board.appendChild(snakeElement);
  });

  rotateSnakeHead(); // Rotate the head of the snake after drawing
}


// Create a snake or food cube/div
function createGameElement(tag, className) {
  const element = document.createElement(tag);
  element.className = className;
  return element;
}

// Set the position of snake or food
function setPosition(element, position) {
  element.style.gridColumn = position.x;
  element.style.gridRow = position.y;
}

// Testing draw function
// draw();

// Draw food function
function drawFood() {
  if (gameStarted) {
    const foodElement = createGameElement('div', 'food');
    setPosition(foodElement, food);
    board.appendChild(foodElement);
  }
}

// Generate food
function generateFood() {
  const x = Math.floor(Math.random() * gridSize) + 1;
  const y = Math.floor(Math.random() * gridSize) + 1;
  return { x, y };
}

// Moving the snake
function move() {
  const head = { ...snake[0] };
  switch (direction) {
    case 'up':
      head.y--;
      break;
    case 'down':
      head.y++;
      break;
    case 'left':
      head.x--;
      break;
    case 'right':
      head.x++;
      break;
  }

  snake.unshift(head);

  //   snake.pop();

  if (head.x === food.x && head.y === food.y) {
    food = generateFood();
    increaseSpeed();
    clearInterval(gameInterval); // Clear past interval
    gameInterval = setInterval(() => {
      move();
      checkCollision();
      draw();
    }, gameSpeedDelay);
  } else {
    snake.pop();
  }
}

// Test moving
// setInterval(() => {
//   move(); // Move first
//   draw(); // Then draw again new position
// }, 200);

// Start game function
function startGame() {
  gameStarted = true; // Keep track of a running game
  instructionText.style.display = 'none';
  logo.style.display = 'none';
  gameInterval = setInterval(() => {
    move();
    checkCollision();
    draw();
  }, gameSpeedDelay);
}

// Keypress event listener// Keypress event listener
function handleKeyPress(event) {
  if (
    (!gameStarted && event.code === 'Space') ||
    (!gameStarted && event.key === ' ')
  ) {
    startGame();
  } else {
    let newDirection;
    switch (event.key) {
      case 'ArrowUp':
        newDirection = 'up';
        break;
      case 'ArrowDown':
        newDirection = 'down';
        break;
      case 'ArrowLeft':
        newDirection = 'left';
        break;
      case 'ArrowRight':
        newDirection = 'right';
        break;
    }

    // Only update the direction if it's not directly opposite to the current one
    if (
      (direction === 'up' && newDirection !== 'down') ||
      (direction === 'down' && newDirection !== 'up') ||
      (direction === 'left' && newDirection !== 'right') ||
      (direction === 'right' && newDirection !== 'left')
    ) {
      direction = newDirection;
      rotateSnakeHead(); // Rotate the head of the snake on direction change
    }
  }
}

document.addEventListener('keydown', handleKeyPress);


function rotateSnakeHead() {
  const snakeHead = document.getElementById('firstSnake');
  if (!snakeHead) return;

  let rotation;
  switch (direction) {
    case 'up':
      rotation = 'rotate(270deg)';
      break;
    case 'down':
      rotation = 'rotate(90deg)';
      break;
    case 'left':
      rotation = 'rotate(180deg)';
      break;
    case 'right':
      rotation = 'rotate(0deg)';
      break;
  }
  snakeHead.style.transform = rotation;
}



function increaseSpeed() {
  //   console.log(gameSpeedDelay);
  if (gameSpeedDelay > 150) {
    gameSpeedDelay -= 5;
  } else if (gameSpeedDelay > 100) {
    gameSpeedDelay -= 3;
  } else if (gameSpeedDelay > 50) {
    gameSpeedDelay -= 2;
  } else if (gameSpeedDelay > 25) {
    gameSpeedDelay -= 1;
  }
}

function checkCollision() {
  const head = snake[0];

  if (head.x < 1 || head.x > gridSize || head.y < 1 || head.y > gridSize) {
    resetGame();
  }

  for (let i = 1; i < snake.length; i++) {
    if (head.x === snake[i].x && head.y === snake[i].y) {
      resetGame();
    }
  }
}

function resetGame() {
  updateHighScore();
  stopGame();
  snake = [{ x: 10, y: 10 }];
  food = generateFood();
  direction = 'right';
  gameSpeedDelay = 200;
  updateScore();
}

function updateScore() {
  const currentScore = snake.length - 1;
  score.textContent = currentScore.toString().padStart(3, '0');
}

function stopGame() {
  clearInterval(gameInterval);
  gameStarted = alert('OH! No! The snake has died!',)
  instructionText.style.display = 'block';
  logo.style.display = 'block';
}

function updateHighScore() {
  const currentScore = snake.length - 1;
  if (currentScore > highScore) {
    highScore = currentScore;
    highScoreText.textContent = highScore.toString().padStart(3, '0');
  }
  highScoreText.style.display = 'block';
}



document.addEventListener('touchstart', handleTouchStart, false);
document.addEventListener('touchmove', handleTouchMove, false);

function handleTouchStart(event) {
  touchStartX = event.touches[0].clientX;
  touchStartY = event.touches[0].clientY;
}

function handleTouchMove(event) {
  if (!touchStartX || !touchStartY) {
    return;
  }

  let touchEndX = event.touches[0].clientX;
  let touchEndY = event.touches[0].clientY;

  let dx = touchEndX - touchStartX;
  let dy = touchEndY - touchStartY;

  let newDirection;
  if (Math.abs(dx) > Math.abs(dy)) {
    newDirection = dx > 0 ? 'right' : 'left';
  } else {
    newDirection = dy > 0 ? 'down' : 'up';
  }

  // Only update the direction if it's not directly opposite to the current one
  if (
    (direction === 'up' && newDirection !== 'down') ||
    (direction === 'down' && newDirection !== 'up') ||
    (direction === 'left' && newDirection !== 'right') ||
    (direction === 'right' && newDirection !== 'left')
  ) {
    direction = newDirection;
    rotateSnakeHead(); // Rotate the head of the snake on direction change
  }

  touchStartX = 0;
  touchStartY = 0;

  // Start the game on first touch if it hasn't started yet
  if (!gameStarted) {
    startGame();
  }

  event.preventDefault();
}

instructionText.textContent = 'Tap to start, then swipe to control the snake';