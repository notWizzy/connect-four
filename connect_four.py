# UNC Charlotte
# ITCS 5153 - Applied AI - Fall 2024
# Lab 3
# Adversarial Search / Game Playing
# This module implements Alpha-Beta Pruning and Minimax algorithms for the Connect Four game from the games.py module provided to us from the repository.
# Student ID: 801232155



# Import the required libraries
import tkinter as tk # Import the Tkinter library for the GUI, learned from online resources
from tkinter import ttk # Import the ttk module from tkinter for themed widgets, learned from online resources.
import numpy as np
import copy # Import the copy module to create deep copies of the game state, learned from online resources.
import time # Import to pause time for AI moves.

def create_window():
    # Create the main window for the application
    root = tk.Tk()
    root.title("Connect Four")  # Set the window title

    # Top frame to hold algorithm selection and search depth controls
    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    # Algorithm selection using radio buttons
    algorithm_var = tk.StringVar(value="Alpha-Beta Pruning")  # Variable to store selected algorithm
    tk.Label(top_frame, text="Select Algorithm:").pack(side=tk.LEFT)  # Label for algorithm selection
    # Radio button for Alpha-Beta Pruning algorithm
    tk.Radiobutton(top_frame, text="Alpha-Beta Pruning", variable=algorithm_var, value="Alpha-Beta Pruning").pack(side=tk.LEFT)
    # Radio button for Minimax algorithm
    tk.Radiobutton(top_frame, text="Minimax", variable=algorithm_var, value="Minimax").pack(side=tk.LEFT)

    # Search depth selection using a slider (Scale)
    tk.Label(top_frame, text="Search Depth:").pack(side=tk.LEFT, padx=(20, 0))  # Label for search depth
    search_depth = tk.IntVar(value=3)  # Variable to store search depth (default set to 3)
    # Slider allowing users to select search depth between 1 and 4
    tk.Scale(top_frame, from_=1, to=4, orient=tk.HORIZONTAL, variable=search_depth).pack(side=tk.LEFT)

    # Middle frame to display whose turn it is (User or AI)
    middle_frame = tk.Frame(root)
    middle_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    turn_text = tk.StringVar(value="User's Turn")  # Variable to store turn status
    # Label to show turn status with larger font for visibility
    turn_label = tk.Label(middle_frame, textvariable=turn_text, font=("Helvetica", 16))
    turn_label.pack()

    # Bottom frame to hold the Connect Four grid and the log area
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Frame to contain the Connect Four grid
    grid_frame = tk.Frame(bottom_frame)
    grid_frame.pack(side=tk.TOP, pady=10)
    # Canvas widget to draw the Connect Four grid
    canvas = tk.Canvas(grid_frame, width=400, height=350, highlightthickness=0)  # Width and height adjusted for better visibility
    canvas.pack()
    cell_width = 50   # Width of each cell in the grid
    cell_height = 50  # Height of each cell in the grid
    rows = 6          # Number of rows in the grid
    cols = 7          # Number of columns in the grid
    # Initialize a 2D list to store references to each oval (cell) in the grid
    grid = [[None for _ in range(cols)] for _ in range(rows)]

    # Create the grid of ovals representing empty cells
    for row in range(rows):
        for col in range(cols):
            x1 = col * cell_width + 5  # X-coordinate for the top-left corner of the oval
            y1 = row * cell_height + 5  # Y-coordinate for the top-left corner of the oval
            x2 = x1 + cell_width        # X-coordinate for the bottom-right corner of the oval
            y2 = y1 + cell_height       # Y-coordinate for the bottom-right corner of the oval
            # Draw an oval (circle) for each cell in the grid
            oval = canvas.create_oval(x1, y1, x2, y2, outline="black", fill="white")
            grid[row][col] = oval  # Store the reference to the oval for later updates

    # Initialize the game state: 0 represents an empty cell, 1 for user, and 2 for AI
    game_state = [[0 for _ in range(cols)] for _ in range(rows)]

    user_turn = True  # Flag to indicate if it's currently the user's turn
    game_over = False  # Flag to indicate if the game has ended

    def on_canvas_click(event):
        """Handle the event when the user clicks on the canvas to make a move."""
        nonlocal user_turn, game_over
        if not user_turn or game_over:
            return  # Ignore clicks if it's not the user's turn or the game is over
        col = event.x // cell_width  # Determine which column was clicked based on the x-coordinate
        if col >= cols:
            return  # Ignore clicks outside the grid
        # Iterate from the bottom row upwards to find the first empty cell in the selected column
        for row in reversed(range(rows)):
            if game_state[row][col] == 0:
                game_state[row][col] = 1  # Mark the cell as occupied by the user
                canvas.itemconfig(grid[row][col], fill="red")  # Change the cell color to red for the user
                # Log the user's move with position, time, and nodes explored
                log_text.insert(tk.END, f"User Move: ({row + 1}, {col + 1}), Time: 0.23 sec, Nodes Explored: 0\n")
                turn_text.set("AI's Turn")  # Update the turn status to AI's turn
                user_turn = False  # Set flag to indicate it's now AI's turn
                check_game_over()  # Check if the user's move has ended the game
                if not user_turn and not game_over:
                    # Schedule the AI to make its move after a short delay (500 ms)
                    root.after(500, ai_move)
                break  # Exit the loop after placing the disc
        else:
            # If the column is full, inform the user via the log
            log_text.insert(tk.END, f"Column {col + 1} is full. Choose another column.\n")

    # Bind the left mouse button click event to the on_canvas_click function
    canvas.bind("<Button-1>", on_canvas_click)

    # Frame to hold the log area with a scrollbar
    log_frame = tk.Frame(bottom_frame)
    log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)  # Text widget to display logs
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(log_frame, command=log_text.yview)  # Scrollbar for the log
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=scrollbar.set)  # Connect the scrollbar to the text widget

    # Frame to hold the control buttons at the bottom
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    # Inner frame to center the buttons horizontally within the button_frame
    inner_button_frame = tk.Frame(button_frame)
    inner_button_frame.pack()

    def start_new_game():
        """Reset the game to start a completely new game, clearing the log."""
        nonlocal user_turn, game_state, game_over
        log_text.delete("1.0", tk.END)  # Clear all text in the log
        log_text.insert(tk.END, "Starting a new game...\n")  # Log the start of a new game
        # Reset all cells in the grid to empty
        for row in range(rows):
            for col in range(cols):
                canvas.itemconfig(grid[row][col], fill="white")  # Reset cell color to white
                game_state[row][col] = 0  # Mark cell as empty in the game state
        turn_text.set("User's Turn")  # Set turn status to user's turn
        user_turn = True  # Indicate it's the user's turn
        game_over = False  # Reset the game over flag

    def restart_game():
        """Restart the current game by resetting the board without clearing the log."""
        nonlocal user_turn, game_state, game_over
        log_text.insert(tk.END, "Restarting the current game...\n")  # Log the restart action
        # Reset all cells in the grid to empty
        for row in range(rows):
            for col in range(cols):
                canvas.itemconfig(grid[row][col], fill="white")  # Reset cell color to white
                game_state[row][col] = 0  # Mark cell as empty in the game state
        turn_text.set("User's Turn")  # Set turn status to user's turn
        user_turn = True  # Indicate it's the user's turn
        game_over = False  # Reset the game over flag

    def exit_program():
        """Exit the application gracefully."""
        root.quit()

    # Create and pack the control buttons within the inner_button_frame
    tk.Button(inner_button_frame, text="New Game", command=start_new_game).pack(side=tk.LEFT, padx=5)
    tk.Button(inner_button_frame, text="Restart Current Game", command=restart_game).pack(side=tk.LEFT, padx=5)
    tk.Button(inner_button_frame, text="Exit", command=exit_program).pack(side=tk.LEFT, padx=5)

    # ------------------------ Game Logic Functions ------------------------

    def to_move(state):
        """
        Determine which player's turn it is based on the current game state.
        Returns 1 for user and 2 for AI.
        """
        count = sum(cell != 0 for row in state for cell in row)  # Count total non-empty cells
        return 1 if count % 2 == 0 else 2  # Even count means user’s turn; odd means AI’s turn

    def actions(state):
        """
        Return a list of valid columns (0-indexed) where a disc can be dropped.
        A column is valid if the top cell is empty.
        """
        return [col for col in range(cols) if state[0][col] == 0]

    def result(state, action, player):
        """
        Return the new state after applying the given action (dropping a disc into a column).
        Copies the current state and updates it with the player's disc.
        """
        new_state = copy.deepcopy(state)  # Create a deep copy of the current state
        for row in reversed(range(rows)):  # Start from the bottom row
            if new_state[row][action] == 0:  # Find the first empty cell in the column
                new_state[row][action] = player  # Place the player's disc
                break
        return new_state  # Return the updated state

    def check_win(state, player):
        """
        Check if the specified player has four discs in a row (horizontally, vertically, or diagonally).
        Returns True if the player has won, else False.
        """
        # Check horizontal locations for a win
        for row in range(rows):
            for col in range(cols - 3):
                if all(state[row][col + i] == player for i in range(4)):
                    return True

        # Check vertical locations for a win
        for col in range(cols):
            for row in range(rows - 3):
                if all(state[row + i][col] == player for i in range(4)):
                    return True

        # Check positively sloped diagonals for a win
        for row in range(rows - 3):
            for col in range(cols - 3):
                if all(state[row + i][col + i] == player for i in range(4)):
                    return True

        # Check negatively sloped diagonals for a win
        for row in range(3, rows):
            for col in range(cols - 3):
                if all(state[row - i][col + i] == player for i in range(4)):
                    return True

        return False  # No win found

    def terminal_test(state):
        """
        Check if the game has reached a terminal state (win for any player or a full board).
        Returns True if the game is over, else False.
        """
        return (check_win(state, 1) or  # User wins
                check_win(state, 2) or  # AI wins
                all(state[0][col] != 0 for col in range(cols)))  # Draw (board is full)

    def evaluate_window(window, player):
        """
        Evaluate a window of four cells and assign a score based on the number of
        player’s and opponent’s discs in the window.
        """
        score = 0
        opponent = 1 if player == 2 else 2  # Determine the opponent's identifier

        if window.count(player) == 4:
            score += 100  # Favor winning moves
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 5  # Favor moves that can lead to a win
        elif window.count(player) == 2 and window.count(0) == 2:
            score += 2  # Slightly favor moves that create potential

        if window.count(opponent) == 3 and window.count(0) == 1:
            score -= 4  # Penalize if opponent can win in the next move

        return score  # Return the computed score for the window

    def evaluate(state, player):
        """
        Evaluate the entire board state and return a score indicating how favorable
        the state is for the specified player.
        """
        score = 0

        # Score the center column higher to encourage control of the center
        center_column = [state[row][cols // 2] for row in range(rows)]
        center_count = center_column.count(player)
        score += center_count * 3  # Increase score based on center control

        # Score horizontal windows
        for row in range(rows):
            row_array = state[row]
            for col in range(cols - 3):
                window = row_array[col:col + 4]  # Extract a window of four cells
                score += evaluate_window(window, player)  # Add the window's score

        # Score vertical windows
        for col in range(cols):
            col_array = [state[row][col] for row in range(rows)]
            for row in range(rows - 3):
                window = col_array[row:row + 4]  # Extract a vertical window of four cells
                score += evaluate_window(window, player)  # Add the window's score

        # Score positively sloped diagonal windows
        for row in range(rows - 3):
            for col in range(cols - 3):
                window = [state[row + i][col + i] for i in range(4)]  # Diagonal from top-left to bottom-right
                score += evaluate_window(window, player)  # Add the window's score

        # Score negatively sloped diagonal windows
        for row in range(3, rows):
            for col in range(cols - 3):
                window = [state[row - i][col + i] for i in range(4)]  # Diagonal from bottom-left to top-right
                score += evaluate_window(window, player)  # Add the window's score

        return score  # Return the total score for the state

    def utility(state, player):
        """
        Determine the utility value of the state for the specified player.
        Returns a high positive value for a win, a high negative value for a loss,
        and the evaluated score for non-terminal states.
        """
        if check_win(state, player):
            return 100  # High utility for winning
        elif check_win(state, 1 if player == 2 else 2):
            return -100  # High negative utility for losing
        else:
            return evaluate(state, player)  # Use evaluation function for non-terminal states

    # Minimax Algorithm Implementation
    def minmax_decision(state, game, player, depth, nodes_explored):
        """
        Determine the best move for the AI using the Minimax algorithm.
        Searches forward up to the specified depth and returns the best column to play.
        """
        def max_value(state, depth_remaining):
            nodes_explored[0] += 1  # Increment nodes explored counter
            if terminal_test(state) or depth_remaining == 0:
                return utility(state, player)  # Return utility if terminal state or depth limit reached
            v = -np.inf  # Initialize maximum value
            for a in actions(state):
                # Recursively call min_value for each possible action
                v = max(v, min_value(result(state, a, 2), depth_remaining - 1))
            return v  # Return the highest value found

        def min_value(state, depth_remaining):
            nodes_explored[0] += 1  # Increment nodes explored counter
            if terminal_test(state) or depth_remaining == 0:
                return utility(state, player)  # Return utility if terminal state or depth limit reached
            v = np.inf  # Initialize minimum value
            for a in actions(state):
                # Recursively call max_value for each possible action
                v = min(v, max_value(result(state, a, 1), depth_remaining - 1))
            return v  # Return the lowest value found

        # Choose the action with the highest min_value
        return max(actions(state), key=lambda a: min_value(result(state, a, 2), depth))

    # Alpha-Beta Pruning Algorithm Implementation
    def alpha_beta_search(state, game, player, depth, nodes_explored):
        """
        Determine the best move for the AI using the Alpha-Beta Pruning algorithm.
        Searches forward up to the specified depth and returns the best column to play.
        """
        def max_value(state, alpha, beta, depth_remaining):
            nodes_explored[0] += 1  # Increment nodes explored counter
            if terminal_test(state) or depth_remaining == 0:
                return utility(state, player)  # Return utility if terminal state or depth limit reached
            v = -np.inf  # Initialize maximum value
            for a in actions(state):
                # Recursively call min_value with updated alpha and beta
                v = max(v, min_value(result(state, a, 2), alpha, beta, depth_remaining - 1))
                if v >= beta:
                    return v  # Beta cutoff
                alpha = max(alpha, v)  # Update alpha
            return v  # Return the highest value found

        def min_value(state, alpha, beta, depth_remaining):
            nodes_explored[0] += 1  # Increment nodes explored counter
            if terminal_test(state) or depth_remaining == 0:
                return utility(state, player)  # Return utility if terminal state or depth limit reached
            v = np.inf  # Initialize minimum value
            for a in actions(state):
                # Recursively call max_value with updated alpha and beta
                v = min(v, max_value(result(state, a, 1), alpha, beta, depth_remaining - 1))
                if v <= alpha:
                    return v  # Alpha cutoff
                beta = min(beta, v)  # Update beta
            return v  # Return the lowest value found

        # Initialize alpha and beta values
        best_score = -np.inf
        beta_val = np.inf
        best_action = None
        # Iterate through all possible actions to find the best one using alpha-beta pruning
        for a in actions(state):
            v = min_value(result(state, a, 2), best_score, beta_val, depth)
            if v > best_score:
                best_score = v  # Update the best score
                best_action = a  # Update the best action
        return best_action  # Return the best action found

    def get_immediate_threat(state, player, nodes_explored):
        """
        Check if the opponent is about to win in the next move.
        If so, return the column to block; otherwise, return None.
        """
        opponent = 1 if player == 2 else 2  # Determine the opponent's identifier
        for col in actions(state):
            nodes_explored[0] += 1  # Increment nodes explored counter for each checked action
            temp_state = result(state, col, opponent)  # Simulate the opponent's move
            if check_win(temp_state, opponent):
                return col  # Return the column that needs to be blocked
        return None  # No immediate threat detected

    def ai_move():
        """Handle the AI's move, including threat detection and selecting the best move."""
        nonlocal user_turn, game_over
        if terminal_test(game_state):
            return  # Do nothing if the game is already over

        # Retrieve the selected algorithm and search depth from the UI controls
        selected_algorithm = algorithm_var.get()
        depth = search_depth.get()

        # Start timing the AI's decision-making process
        start_time = time.time()
        nodes_explored = [0]  # Initialize nodes explored counter

        # Check if the user has an immediate threat that needs to be blocked
        blocking_move = get_immediate_threat(game_state, 2, nodes_explored)
        if blocking_move is not None:
            best_move = blocking_move  # Prioritize blocking the user's winning move
            time_taken = time.time() - start_time  # Calculate the time taken for decision
            # Find the row in the selected column where the AI will place its disc
            for row in reversed(range(rows)):
                if game_state[row][best_move] == 0:
                    game_state[row][best_move] = 2  # Mark the cell as occupied by the AI
                    canvas.itemconfig(grid[row][best_move], fill="yellow")  # Change cell color to yellow for AI
                    # Log the AI's move with position, time taken, and nodes explored
                    log_text.insert(tk.END, f"AI Move: ({row + 1}, {best_move + 1}), Time: {time_taken:.2f} sec, Nodes Explored: {nodes_explored[0]}\n")
                    turn_text.set("User's Turn")  # Update turn status back to the user
                    user_turn = True  # Set flag to indicate it's the user's turn
                    check_game_over()  # Check if the AI's move has ended the game
                    break
        else:
            # If there's no immediate threat, use the selected algorithm to determine the best move
            if selected_algorithm == "Minimax":
                best_move = minmax_decision(game_state, None, 2, depth, nodes_explored)  # Use Minimax
            else:
                best_move = alpha_beta_search(game_state, None, 2, depth, nodes_explored)  # Use Alpha-Beta Pruning

            time_taken = time.time() - start_time  # Calculate the time taken for decision

            if best_move is not None:
                # Find the row in the chosen column where the AI will place its disc
                for row in reversed(range(rows)):
                    if game_state[row][best_move] == 0:
                        game_state[row][best_move] = 2  # Mark the cell as occupied by the AI
                        canvas.itemconfig(grid[row][best_move], fill="yellow")  # Change cell color to yellow for AI
                        # Log the AI's move with position, time taken, and nodes explored
                        log_text.insert(tk.END, f"AI Move: ({row + 1}, {best_move + 1}), Time: {time_taken:.2f} sec, Nodes Explored: {nodes_explored[0]}\n")
                        turn_text.set("User's Turn")  # Update turn status back to the user
                        user_turn = True  # Set flag to indicate it's the user's turn
                        check_game_over()  # Check if the AI's move has ended the game
                        break
            else:
                # If the AI couldn't determine a move (which shouldn't happen), log the issue
                log_text.insert(tk.END, "AI could not determine a move.\n")
                turn_text.set("User's Turn")  # Update turn status back to the user
                user_turn = True  # Set flag to indicate it's the user's turn

    def check_game_over():
        """
        Check if the game has ended due to a win or a draw.
        Update the log and turn status accordingly.
        """
        nonlocal game_over
        if check_win(game_state, 1):
            log_text.insert(tk.END, "Game Over: User Wins!\n")  # Log user's win
            turn_text.set("Game Over: User Wins!")  # Update turn status
            user_turn = False  # Disable further moves
            game_over = True  # Set game over flag
        elif check_win(game_state, 2):
            log_text.insert(tk.END, "Game Over: AI Wins!\n")  # Log AI's win
            turn_text.set("Game Over: AI Wins!")  # Update turn status
            user_turn = False  # Disable further moves
            game_over = True  # Set game over flag
        elif all(game_state[0][col] != 0 for col in range(cols)):
            log_text.insert(tk.END, "Game Over: Draw\n")  # Log a draw
            turn_text.set("Game Over: Draw")  # Update turn status
            user_turn = False  # Disable further moves
            game_over = True  # Set game over flag

    # Start the Tkinter event loop to run the application
    root.mainloop()

# Call the create_window function to launch the game
create_window()