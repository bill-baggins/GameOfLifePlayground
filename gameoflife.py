# Conway's Game of Life implemented in pygame.
# By: Bill Baggins
# Version 1.0

# TODO: Features to be implemented:
#       1) Improve the readability of the text on the window.
#       2) Add a menu where the user can change screen resolution, begin the game, and end the game.
#       3) Add a cropping function, where you can drag a rectangle outline over an area and drag an
#       pattern to a place. This rectangle will have collision detection with the window edge, so that
#       a user cannot drag the pattern outside the bounds of the window.

import pygame
import json
from pygame.constants import *

# Initialize pygame and the pygame.font libraries.
pygame.init()
pygame.font.init()

# Global file variables.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
SKYBLUE = (0, 255, 255)
YELLOW = (255, 255, 0)

# Key map that stores boards to a key. "49" is the key 1, "50" is the key 2, etc.
key_map = {"49": [], "50": [], "51": [], "52": [], "53": [], "54": [], "55": [], "56": [], "57": []}

# Load the json file into a variable called "temp".
temp = None
try:
    with open("saved_boards.json") as file:
        temp = json.load(file)
except FileNotFoundError:
    temp = key_map

# If the json file is missing entries, the empty key_map above will be used.
if len(temp.keys()) == 9:
    print("saved_boards.json loaded successfully.")
    key_map = temp


# Function that creates a list of strings to be drawn on the screen.
def save_slots_list():
    res = []
    for i in range(len(key_map.keys())):
        if len(key_map[str(49 + i)]) != 0:
            res.append(f"Slot {i + 1}: {'Filled'}")
        else:
            res.append(f"Slot {i + 1}: {'Empty'}")
    return res


# Menu loop. This will have the logic associated with the menu.
def menu_loop():
    settings = (1920, 1080, "Conway's Game of Life", False, 1)
    return settings


# Main game loop.
def main_loop(width, height, caption, fullscreen=False, cell_scale=1.0, fps=30):
    # Pygame clock for keeping track of time; used for dt.
    clock = pygame.time.Clock()
    ms = 0
    dt = 0
    screen_fps = fps
    low_screen_fps = 10

    # Window settings. The size and height of the display are set here.
    size = (width, height)
    screen = pygame.display.set_mode(size, FULLSCREEN if fullscreen else 0, vsync=False)
    pygame.display.set_caption(caption)

    # Load the images. They are converted to increase performance in drawing.
    # The window's icon is also set here.
    blue_cell = pygame.image.load("resources/blue_cell.bmp").convert()
    dead_cell = pygame.image.load("resources/dead_cell.bmp").convert()
    pygame.display.set_icon(blue_cell)

    # Changes the size of the cells if the cell_scale is not set to 1
    if cell_scale != 1:
        new_width = int(blue_cell.get_width() * cell_scale)
        new_height = int(blue_cell.get_height() * cell_scale)
        blue_cell = pygame.transform.scale(blue_cell, (new_width, new_height))
        dead_cell = pygame.transform.scale(dead_cell, (new_width, new_height))

    # Size of the grids below.
    grid_x = (size[0] // blue_cell.get_width()) + 2
    grid_y = (size[1] // blue_cell.get_height()) + 2

    # Grids that will hold the cells.
    initial_grid = [0 for _ in range(int(grid_x * grid_y))]
    output_grid = [0 for _ in range(int(grid_x * grid_y))]

    # Store a pygame.font.Font object into variable 'text'. This will be used for all instances of
    # text.
    text = pygame.font.Font(pygame.font.get_default_font(), 20)

    # Tuple of all of the available controls.
    controls = ("Controls:", "Spacebar: Pause/Unpause", "Escape: Close Window", "Left Mouse Button: Turn cell on",
                "Right Mouse Button: Turn cell off", "E: Clear the board",
                "Up Arrow: Speed up refresh rate", "Down Arrow: Slow down refresh rate",
                "R: Reset refresh rate", "S: Toggle Save Override", "D: Toggle Delete Mode")
    num_of_controls = len(controls)

    # Renders each control in the tuple, which will be drawn later.
    text_controls = [text.render(control, False, SKYBLUE) for control in controls]

    # Renders the "Paused" text that is seen in the top-left corner of the screen.
    text_paused = text.render("Paused", False, SKYBLUE)

    # Save Override text. Lots of text to render here.
    text_os = "Save override is on. Press a key from 1-9 to bind your current board to that key."
    text_override_save = text.render(text_os, False, SKYBLUE)
    save_slots = save_slots_list()
    text_save_slots_list = [text.render(save_slot, False, SKYBLUE) for save_slot in save_slots]

    # Delete mode text.
    text_dlt = "Delete mode is on. Press a key from 1-9 to delete your save at that key."
    text_delete = text.render(text_dlt, False, RED)

    # Current slot you are on text.
    current_slot = f"Current slot: None"
    text_current_slot = text.render(current_slot, False, SKYBLUE)

    # Bunch of booleans that do various things.
    override_save_mode = False
    delete_save_mode = False
    game_paused = True
    counter = 0
    limit = 4
    MOUSE_DOWN = False

    # Game loop begins here.
    running = True
    while running:
        dt = ms / 1000.0

        # Get user input.
        for event in pygame.event.get():

            # If the player clicks the red X on the window, it will close the window.
            if event.type == QUIT:
                running = False
                break

            # Gets any key-down event.
            if event.type == KEYDOWN:
                event_key_str = str(event.key)
                if event.key == K_ESCAPE:
                    running = False
                    break

                # Erases the current board.
                if event.key == K_e and game_paused:
                    initial_grid = [0 for _ in range(int(grid_x * grid_y))]
                    output_grid = [0 for _ in range(int(grid_x * grid_y))]

                # Toggles pause/unpause.
                if event.key == K_SPACE and not override_save_mode and not delete_save_mode:
                    game_paused = not game_paused

                # Control how quickly the screen refreshes.
                if event.key == K_r:
                    limit = 4
                elif event.key == K_UP and limit != 2:
                    limit -= 1
                elif event.key == K_DOWN and limit < 15:
                    limit += 1

                # A bunch of special events that only get called if the game is paused.
                if game_paused:

                    # Toggles save override mode.
                    if event.key == K_s and not delete_save_mode:
                        override_save_mode = not override_save_mode

                    # Toggles on "delete" mode. Game must be paused while this takes place.
                    if event.key == K_d and not override_save_mode:
                        delete_save_mode = not delete_save_mode

                    # Saves the current board to the key_map dict. Game must be paused for this. Once you save
                    # a board to the key_map dict, the override_save_mode will toggle off.
                    if event_key_str in key_map.keys() and override_save_mode:
                        # Totally not confusing list comprehension that appends the coordinates of each live cell
                        # to the list in the key_map dictionary.
                        key_map[event_key_str] = [(x, y) for x in range(grid_x) for y in range(grid_y)
                                                  if initial_grid[y * grid_x + x] == 1]
                        save_slots = save_slots_list()
                        save_slot_index = event.key - 49

                        current_slot = f"Current slot: {save_slot_index + 1}"
                        text_current_slot = text.render(current_slot, False, SKYBLUE)

                        txt = f"Slot {save_slot_index + 1}: Filled"
                        text_save_slots_list[save_slot_index] = text.render(txt, False, SKYBLUE)
                        override_save_mode = not override_save_mode

                    # Loads a board from key_map. It will not load if the board at the pressed key is empty.
                    # This will also erase the current board, so as to prevent mixing of the initial_grid and
                    # the board at key_map[key].
                    if event_key_str in key_map.keys():
                        if not override_save_mode and not delete_save_mode:
                            current_slot = f"Current slot: {int(event_key_str) - 49 + 1}"
                            text_current_slot = text.render(current_slot, False, SKYBLUE)

                            if len(key_map[event_key_str]) != 0:
                                initial_grid = [0 for _ in range(grid_x * grid_y)]
                                for cell_loc in key_map[event_key_str]:
                                    if cell_loc[0] < grid_x and cell_loc[1] < grid_y:
                                        initial_grid[cell_loc[1] * grid_x + cell_loc[0]] = 1

                    # Allows you to delete boards from the save slots. Once you delete a board, the functionality
                    # will toggle off.
                    if delete_save_mode:
                        if event_key_str in key_map.keys():
                            if key_map[event_key_str]:
                                key_map[event_key_str] = []
                                save_slots = save_slots_list()
                                save_slot_index = event.key - 49

                                txt = f"Slot {save_slot_index + 1}: Empty"
                                text_save_slots_list[save_slot_index] = text.render(txt, False, SKYBLUE)
                                delete_save_mode = not delete_save_mode

            # These two if statements detect whenever the button is down or up.
            if event.type == MOUSEBUTTONDOWN:
                if game_paused:
                    MOUSE_DOWN = True
            if event.type == MOUSEBUTTONUP:
                if game_paused:
                    MOUSE_DOWN = False

        # Get continuous user input to draw cells.
        if game_paused and MOUSE_DOWN:
            mouse_pos = pygame.mouse.get_pos()
            button = pygame.mouse.get_pressed(3)
            x = (mouse_pos[0] // dead_cell.get_width()) + 1
            y = (mouse_pos[1] // dead_cell.get_height()) + 1
            if button[0]:
                initial_grid[y * grid_x + x] = 1
            elif button[2]:
                initial_grid[y * grid_x + x] = 0

        # Update the screen. This nested for-loop contains all of the important logic that makes Conway's
        # Game of Life work.
        counter += 1
        if not game_paused and counter >= limit:

            # The nested for-loop that updates the grid every frame.
            for x in range(1, grid_x - 1):
                for y in range(1, grid_y - 1):

                    total = initial_grid[(y - 1) * grid_x + (x - 1)] + initial_grid[(y - 1) * grid_x + x] + \
                            initial_grid[(y - 1) * grid_x + (x + 1)] + initial_grid[y * grid_x + (x - 1)] + \
                            initial_grid[y * grid_x + (x + 1)] + initial_grid[(y + 1) * grid_x + (x - 1)] + \
                            initial_grid[(y + 1) * grid_x + x] + initial_grid[(y + 1) * grid_x + (x + 1)]

                    # The core logic that makes Conway's Game of Life work.
                    if initial_grid[y * grid_x + x] == 1:
                        if total == 2 or total == 3:
                            output_grid[y * grid_x + x] = 1
                        else:
                            output_grid[y * grid_x + x] = 0
                    else:
                        if total == 3:
                            output_grid[y * grid_x + x] = 1

            # Copy the output grid to the initial_grid.
            initial_grid = output_grid
            output_grid = [0 for _ in range(int(grid_x * grid_y))]
            counter = 0

        # Draw to the screen
        screen.fill(WHITE)
        for x in range(1, grid_x - 1):
            for y in range(1, grid_y - 1):
                if initial_grid[y * grid_x + x] == 0:
                    screen.blit(dead_cell, ((x - 1) * dead_cell.get_width(), (y - 1) * dead_cell.get_height()))
                elif initial_grid[y * grid_x + x] == 1:
                    screen.blit(blue_cell, ((x - 1) * blue_cell.get_width(), (y - 1) * blue_cell.get_height()))

        # Draw various things to the screen if it gets paused.
        if game_paused:

            # Draw text that tells the user the game is paused.
            screen.blit(text_paused, (0, 0))

            # Draw the text controls.
            for i in range(len(text_controls)):
                screen.blit(text_controls[i], (0, (20 * i) + (screen.get_height() - (20 * num_of_controls))))

            # Draws yellow text at the top right corner of the screen. telling the player
            # that the "override save mode" is turned on.
            if override_save_mode and not delete_save_mode:
                screen.blit(text_override_save, (screen.get_width() - (len(text_os) * 10), 0))

            # Draws red text at the top right corner of the screen, telling the player that delete-mode is on.
            if delete_save_mode and not override_save_mode:
                screen.blit(text_delete, (screen.get_width() - len(text_dlt) * 10, 0))

            # Draws the slots and whether or not they are filled at the bottom right of the screen.
            for i in range(len(text_save_slots_list)):
                slot = text_save_slots_list[i]
                screen.blit(slot, (screen.get_width() - (len(save_slots[i]) * 10),
                                   (20 * i) + (screen.get_height() - (20 * len(text_save_slots_list)))))

            # Draws the current slot you are on at the top right of the screen.
            screen.blit(text_current_slot, (screen.get_width() - len(current_slot) * 10, 20))

        if game_paused and not MOUSE_DOWN:
            ms = clock.tick(low_screen_fps)
        else:
            ms = clock.tick(screen_fps)
        pygame.display.update()

    # Copy the contents of key_map to the json file.
    with open("saved_boards.json", "w") as f:
        json.dump(key_map, f)


if __name__ == '__main__':
    # Begin the menu loop (will eventually be implemented)
    # window_settings = menu_loop()

    w, h = 1440, 810
    c = "Conway's Game of Life"
    f = False
    s = 0.75
    s_fps = 60

    main_loop(w, h, c, f, s, s_fps)

    # After the game loop, quit the pygame and pygame.font libraries.
    pygame.quit()
    pygame.font.quit()
