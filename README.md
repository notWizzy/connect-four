Game Controls
Selecting Algorithm:

Choose between Alpha-Beta Pruning and Minimax using the radio buttons at the top of the window.
Setting Search Depth:

Use the slider labeled "Search Depth" to set the AI's difficulty level:
1: Easiest AI, quick responses.
4: Hardest AI, more strategic and longer computation times.
Making a Move:

Click on the desired column in the grid to drop your disc. The disc will occupy the lowest available space in that column.
Viewing Move Logs:

The log area at the bottom displays each move made by both the user and AI, along with computation time and nodes explored.
Control Buttons:

New Game: Starts a completely new game and clears the move log.
Restart Current Game: Resets the board without clearing the existing move log.
Exit: Closes the application.
Gameplay
Objective: Connect four of your discs in a row horizontally, vertically, or diagonally before the AI does.
Turns: The user always goes first, followed by the AI.
Winning the Game: The game ends when a player connects four discs or when the board is full, resulting in a draw.
How It Works
Game Mechanics
The game board consists of a 6-row by 7-column grid. Players take turns dropping discs into the columns, and the discs stack from the bottom up. The first player to align four discs in a row horizontally, vertically, or diagonally wins the game.

AI Algorithms
Minimax Algorithm
The Minimax algorithm simulates all possible moves up to a certain depth to determine the most advantageous move for the AI. It assumes that the opponent (user) will also play optimally. The AI evaluates the game state by assigning scores based on potential winning combinations.

Alpha-Beta Pruning
Alpha-Beta Pruning is an optimization of the Minimax algorithm that eliminates branches in the game tree that don't need to be explored because they cannot possibly affect the final decision. This reduces the number of nodes the AI needs to evaluate, leading to faster decision-making, especially at higher search depths.

Immediate Threat Detection
Before the AI makes its move, it checks if the user has an immediate winning move in the next turn. If such a threat is detected, the AI prioritizes blocking it to prevent the user from winning.

Move Logging
Each move made by both the user and AI is logged with the following details:

Position: The row and column where the disc was placed.
Time Taken: The computation time the AI took to decide on its move.
Nodes Explored: The number of nodes the AI evaluated during its decision-making process.
