# Donkey Kong V2 - Implementation Requirements

This document provides a highly detailed, step-by-step guide on how to code the Pygame version of Donkey Kong from absolute scratch. Refer to this when you get stuck or need to know how the systems tie together.

---

## Step 1: Settings and Configuration (`settings.py`)
Create a file to store all global variables so you don't have "magic numbers" in your code.
1. **Screen Size**: Define `TILE_SIZE = 16`. The window size should be `WIDTH = 1280` and `HEIGHT = 528`. The maximum world width (for scrolling) will be `WORLD_WIDTH = 200 * 16`.
2. **Physics Constants**: Define `GRAVITY = 0.5`, `JUMP_POWER = -10`, `PLAYER_SPEED = 4`.
3. **Game Rules**: Define `MAX_LEVEL = 10`, `COINS_FOR_LIFE = 50`.

---

## Step 2: Level Generation (`level_generator.py`)
You will build a procedural map generator that outputs a 2D matrix (a list of lists containing strings like `"x"`, `"H"`, etc.) for the Pygame engine to read.
1. **Initialize the Matrix**: Create a 2D list of `WORLD_WIDTH // 16` columns and `HEIGHT // 16` rows filled with empty spaces `" "`.
2. **Create Floors**: Loop through the rows. Every 4 or 5 rows, fill the entire row with `"x"` (platforms). 
3. **Random Gaps**: For each floor row, randomly replace small chunks of `"x"` with `" "` to create gaps the player must jump over.
4. **Create Ladders**: For each floor, randomly pick 2-3 column indexes (making sure at least one is on the far left and one is on the far right). Fill the rows connecting the current floor to the floor above it with `"H"` to create ladders.
5. **Portals and Queens**: 
   - If `level < 10`: Randomly pick an empty space (`" "`) in the top half of the map that is NOT directly touching a floor or ladder, and set it to `"P"` (Portal).
   - If `level == 10`: Place the Queen `"Q"` in a custom built "cage" made of `"x"` tiles at the top center of the map.
6. **Return the Matrix**: Provide a function `generate_level(level_num)` that runs this logic and returns the matrix.

---

## Step 3: Building the Sprites (`sprites.py`)
You will use `pygame.sprite.Sprite` for all game objects.

### 3.1 Static Sprites (Platforms, Ladders, Coins, Portals)
- Create a `Platform` class. In `__init__(self, x, y)`, set `self.image = pygame.image.load('assets/platform.png')` and set `self.rect = self.image.get_rect(topleft=(x,y))`.
- Do the same for `Ladder`, `Coin`, `Portal`, and `Queen`.

### 3.2 Dynamic Sprites (Fireballs)
- **Physics**: Fireballs need `self.vel_x` and `self.vel_y`. Apply `GRAVITY` to `self.vel_y` every frame.
- **Collision**: In their `update(self, platforms)` method, check `colliderect` against platforms. If they hit a floor, set `self.vel_y = -bounce_power` (make them bounce!). Reverse `self.vel_x` if they hit a wall.

### 3.3 The Donkey
- **Patrol Zone**: When initialized, give the donkey a `min_x` and `max_x` that keeps him in the center of the map.
- **Movement**: Give the donkey a `self.speed`. If `self.rect.x` hits `min_x` or `max_x`, reverse its speed.
- **Timer**: Add an `update()` method that ticks a variable `self.timer`. When `self.timer > 120` (2 seconds at 60 FPS), spawn a `Fireball` and reset the timer.

### 3.4 The Player (Prince)
This is the most complex class. You have multiple animation frames to load!
- **Loading Assets**: Load all the prince images and remove the green background using `set_colorkey()`:
  ```python
  self.idle_image = pygame.image.load('assets/prince_idle_1789047057268.png').convert()
  self.idle_image.set_colorkey((0, 255, 0)) # Assuming bright green background
  # Load run_1, run_2, climb_1 the same way. 
  # Note: You can use pygame.transform.flip(image, True, False) to create the left-facing versions!
  self.image = self.idle_image
  ```
- **Animation State**: Keep a timer (e.g., `self.anim_tick`) to swap `self.image` between `run_1` and `run_2` every few frames when moving horizontally.
- **State**: Track `self.vel_x`, `self.vel_y`, and a boolean `self.on_ladder`.
- **Horizontal Movement**: Check `pygame.key.get_pressed()`. If `K_a`, `self.vel_x = -PLAYER_SPEED`. If `K_d`, `self.vel_x = PLAYER_SPEED`.
- **Vertical Movement (Gravity)**: If not `self.on_ladder`, add `GRAVITY` to `self.vel_y`.
- **Jumping**: If `K_SPACE` and the player is standing on a platform, set `self.vel_y = JUMP_POWER`.
- **Collision Logic (CRITICAL)**:
  1. Move the player's `self.rect.x` by `self.vel_x`. 
  2. Check for horizontal collisions with platforms. If a collision occurs, snap the player's edge to the platform's edge.
  3. Move the player's `self.rect.y` by `self.vel_y`.
  4. Check for vertical collisions. If falling and hitting a platform, set `self.vel_y = 0` and position the player on top.

---

## Step 4: The Scrolling Camera System
To make the game side-scrolling, you need a camera variable in your main loop to track the player.
1. Initialize `camera_x = 0`.
2. Every frame, update `camera_x` to follow the player:
   `camera_x = player.rect.centerx - (WIDTH // 2)`
3. Keep the camera within the bounds of the level so it doesn't show empty space:
   ```python
   # Max width is WORLD_WIDTH - screen width
   max_camera_x = WORLD_WIDTH - WIDTH
   camera_x = max(0, min(camera_x, max_camera_x))
   ```
4. Whenever you draw a sprite to the screen, subtract `camera_x` from its `rect.x`:
   `screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))`

---

## Step 5: The Main Game Loop (`main_pygame.py`)
This ties everything together.

### 5.1 Initialization
- `pygame.init()`. Set up `screen = pygame.display.set_mode((WIDTH, HEIGHT))`.
- Create a `clock = pygame.time.Clock()`.

### 5.2 State Variables
- `current_level = 1`
- `lives = 3`
- `score = 0`
- `coins = 0`

### 5.3 Loading a Level
Write a function `load_level(level_number)`:
- Call `matrix = generate_level(level_number)` from `level_generator.py`.
- Loop through `matrix` row by row and column by column.
- If you see `"x"`, create a `Platform` sprite at `x = col * 16, y = row * 16`.
- Add all these sprites to Pygame `pygame.sprite.Group()` objects (e.g., `platform_group`, `coin_group`).

### 5.4 The Start Screen / Story Dialog
Before entering the main game loop, you need a blocking loop to show the story:
1. Fill the screen with black: `screen.fill((0, 0, 0))`
2. Render the backstory: "The Queen has been captured by the Donkey!"
3. Render the controls: "A/D to move, W/S to climb, SPACE to jump."
4. Render prompt: "Press any key to start."
5. Use a `while` loop that calls `pygame.event.get()`. If the event is `pygame.KEYDOWN`, `break` out of the loop and proceed to the main game loop.

### 5.5 The `while True:` Loop
Every tick of the game loop should execute in this order:
1. **Events**: `for event in pygame.event.get():` (Handle quitting).
2. **Updates**: Call `player.update()`, `donkey.update()`, `fireballs.update()`.
3. **Interactions**:
   - `pygame.sprite.spritecollide(player, coins_group, True)`: If player touches a coin, remove the coin (`True`), add `+5` to `score`, and add `+1` to `coins`.
   - **Coin Check**: `if coins >= COINS_FOR_LIFE:` -> `lives += 1`, `coins = 0`.
   - `spritecollide(player, fireballs_group)`: If hit, `lives -= 1`, reset player to start.
   - **Portal Check**: `spritecollide(player, portal_group)`: If hit, `current_level += 1`, clear all sprite groups, and call `load_level(current_level)`.
   - **Queen Check**: If `current_level == 10` and player touches the Queen, display "YOU WIN!" and freeze.
4. **Draw HUD**: Use `font = pygame.font.SysFont("Courier", 24)` to render `SCORE`, `LIVES`, `LEVEL`, and `COINS` directly to the screen (do NOT subtract `camera_x` for the HUD, so it stays fixed in the corners).
5. **Draw Sprites**: Loop through `all_sprites_group` and draw them using the camera offset (as explained in Step 4).
6. **Tick**: `pygame.display.flip()` and `clock.tick(60)`.

---

## Step 6: Packaging for Itch.io
Once your game is complete, you can publish it to Itch.io so others can play it!

### 6.1 Play-in-Browser (HTML5 WebAssembly)
This is the most popular option on Itch.io as it doesn't require users to download anything.
1. In your terminal, run: `pip install pygbag`
2. Run the packaging command on your project folder: `pygbag .` (or `pygbag c:\Users\ayushi\games\Donkey-Kong-V2`)
3. `pygbag` will generate a `build/web/` folder containing an HTML5 zip file.
4. Go to your Itch.io project page, upload this zip file, and select the **"This file will be played in the browser"** option.

### 6.2 Standalone Executable (Windows .exe)
For users who want to download and play the game offline:
1. In your terminal, run: `pip install pyinstaller`
2. Bundle your game into a single file by running:
   `pyinstaller --onefile --windowed main_pygame.py`
3. A `dist/` folder will be created containing `main_pygame.exe`. You must copy your `assets/` folder into the `dist/` folder so the executable can find your images!
4. Zip the `.exe` and the `assets/` folder together, and upload that zip to Itch.io as a downloadable Windows game.
