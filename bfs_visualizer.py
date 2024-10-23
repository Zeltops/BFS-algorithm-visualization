from tkinter import messagebox, Tk
import pygame
import sys

# Initialize Pygame
pygame.init()

# Window dimensions
window_width = 800
window_height = 800

# Create the Pygame window
window = pygame.display.set_mode((window_width, window_height))

# Grid dimensions
columns = 50
rows = 50

# Box dimensions
box_width = window_width // columns
box_height = window_height // rows

# Initialize grid, queue, and path lists
grid = []
queue = []
path = []

class Box:
    def __init__(self, i, j):
        self.x = i
        self.y = j
        self.start = False
        self.wall = False
        self.target = False
        self.queued = False
        self.visited = False
        self.neighbours = []
        self.prior = None

    def draw(self, win, color):
        pygame.draw.rect(win, color, (self.x * box_width, self.y * box_height, box_width - 2, box_height - 2))

    def set_neighbours(self):
        if self.x > 0:
            self.neighbours.append(grid[self.x - 1][self.y])
        if self.x < columns - 1:
            self.neighbours.append(grid[self.x + 1][self.y])
        if self.y > 0:
            self.neighbours.append(grid[self.x][self.y - 1])
        if self.y < rows - 1:
            self.neighbours.append(grid[self.x][self.y + 1])


# Initialize Pygame's font module
pygame.font.init()
font = pygame.font.SysFont("Calibri", 24)

# Create Grid
for i in range(columns):
    arr = []
    for j in range(rows):
        arr.append(Box(i, j))
    grid.append(arr)

# Set Neighbours
for i in range(columns):
    for j in range(rows):
        grid[i][j].set_neighbours()

def reset_game():
    """Function to reset the game state."""
    global grid, queue, path
    grid = []
    queue = []
    path = []
    
    # Reinitialize grid and neighbors
    for i in range(columns):
        arr = []
        for j in range(rows):
            arr.append(Box(i, j))
        grid.append(arr)
    
    for i in range(columns):
        for j in range(rows):
            grid[i][j].set_neighbours()

def main():
    # Define reset button properties outside the loop so they can be accessed globally
    button_x = window_width - 200
    button_y = window_height - 120
    button_width = 120
    button_height = 40

    begin_search = False
    target_box_set = False
    searching = True
    start_box_set = False
    target_box = None

    while True:
        for event in pygame.event.get():
            # Quit Window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Mouse Controls
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                i = x // box_width
                j = y // box_height

                # Check if click is inside the black area but not the reset button
                if y > window_height - 180 and not (button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height):
                    continue

                # Set start box
                if event.button == 1:  # Left mouse button click
                    if not start_box_set and not grid[i][j].wall:
                        start_box = grid[i][j]
                        start_box.start = True
                        start_box.visited = True
                        queue.append(start_box)
                        start_box_set = True

                    # Check if reset button is clicked
                    if button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height:
                        reset_game()
                        start_box_set = False
                        target_box_set = False
                        searching = True
                        begin_search = False
                        continue

                # Set target box
                elif event.button == 3:  # Right mouse button click
                    if not target_box_set and not grid[i][j].wall:
                        target_box = grid[i][j]
                        target_box.target = True
                        target_box_set = True

            elif event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()

                # Ignore wall drawing in the black rectangle area, except for the reset button
                if y > window_height - 180 and not (button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height):
                    continue

                # Draw Wall
                if event.buttons[0]:
                    i = x // box_width
                    j = y // box_height
                    grid[i][j].wall = True

            # Start Algorithm
            if event.type == pygame.KEYDOWN and target_box_set:
                begin_search = True

        if begin_search:
            if len(queue) > 0 and searching:
                current_box = queue.pop(0)
                current_box.visited = True
                if current_box == target_box:
                    searching = False
                    while current_box.prior != start_box:
                        path.append(current_box.prior)
                        current_box = current_box.prior
                else:
                    for neighbour in current_box.neighbours:
                        if not neighbour.queued and not neighbour.wall:
                            neighbour.queued = True
                            neighbour.prior = current_box
                            queue.append(neighbour)
            else:
                if searching:
                    Tk().wm_withdraw()
                    messagebox.showinfo("No Solution", "There is no solution!")
                    searching = False

        # Drawing
        window.fill((0, 0, 0))  # Black background

        for i in range(columns):
            for j in range(rows):
                box = grid[i][j]
                box.draw(window, (100, 100, 100))  # Default grid color

                if box.queued:
                    box.draw(window, (200, 0, 0))  # Queued boxes are red
                if box.visited:
                    box.draw(window, (0, 200, 0))  # Visited boxes are green
                if box in path:
                    box.draw(window, (0, 0, 200))  # Path is blue
                if box.start:
                    box.draw(window, (0, 200, 200))  # Start box is cyan
                if box.wall:
                    box.draw(window, (10, 10, 10))  # Walls are black
                if box.target:
                    box.draw(window, (200, 200, 0))  # Target box is yellow

        # Instructions area - Black rectangle
        pygame.draw.rect(window, (0, 0, 0), (0, window_height - 180, window_width, 300))  # Taller black background for instructions

        # Render instructions text
        instructions = [
            "Instructions:",
            "1. Left click to set start",
            "2. Left click and hold to draw walls",
            "3. Right click to set target",
            "4. Press any key to run",
            "5. Click 'Reset' to restart"
        ]
        for i, instruction in enumerate(instructions):
            text_surface = font.render(instruction, True, (255, 255, 255))  # White text
            window.blit(text_surface, (10, window_height - (len(instructions) - i) * 25 - 25))  # Move up by adjusting y-position

        # Draw reset button
        pygame.draw.rect(window, (200, 0, 0), (button_x, button_y, button_width, button_height))  # Bigger reset button
        reset_text = font.render("Reset", True, (255, 255, 255))  # White text for reset button
        window.blit(reset_text, (button_x + (button_width - reset_text.get_width()) // 2, button_y + (button_height - reset_text.get_height()) // 2))  # Center text in button

        pygame.display.update()

main()
