import cv2
import numpy as np
import time
import pygame
import random

# ===========================
# ===== CONFIGURATIONS ======
# ===========================
CAMERA_MODE = False  # True = Demo Mode (no game logic), False = Actual Game Mode

# Game parameters
SENSITIVITY_THRESHOLD = 40
DETECTION_AREA = 2000
GAME_TIMER = 60
GREEN_LIGHT_MIN = 3
GREEN_LIGHT_MAX = 7
RED_LIGHT_DURATION = 5
GRACE_RED = 0.7
PREPARATION_TIME = 10  # Time to wait during the preparation phase

# ===========================
# ===== INITIAL SETUP =======
# ===========================
pygame.mixer.init()
pygame.mixer.music.load('./assets/greenlight.mp3')
redlight_sound = pygame.mixer.Sound('./assets/redlight.mp3')
lose_sound = pygame.mixer.Sound('./assets/lose.mp3')
win_sound = pygame.mixer.Sound('./assets/win.mp3')
preparation_sound = pygame.mixer.Sound('./assets/preparation.mp3')

def game_loop():
    # Camera capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return
    
    # Background subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2(history=5, varThreshold=SENSITIVITY_THRESHOLD)

    # ===========================
    # === Window / Layout Setup =
    # ===========================
    # Create a full-screen window
    cv2.namedWindow("Game Window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Game Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # You can adjust these if your system’s screen is different or if you want a smaller window
    screen_width = 1920
    screen_height = 1080

    # We'll reserve a "title bar" at the top for text (time left, game state, or "Demo Mode").
    title_bar_height = 120
    # The remaining area will be used for the 2×2 grid
    grid_height = screen_height - title_bar_height
    cell_width = screen_width // 2
    cell_height = grid_height // 2

    # ===========================
    # ===== Game State Vars =====
    # ===========================
    game_active = False
    game_over = False
    game_state = "Idle"
    start_time = 0
    last_state_change_time = 0
    red_light_start_time = 0

    print("Press 'R' to start the game (if not in CAMERA_MODE). Press ESC to exit.")

    while True:
        # Grab a camera frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera. Exiting...")
            break

        # Create the top title bar
        # We'll fill it with a dark background (e.g., grey) so white text is visible
        title_bar = np.full((title_bar_height, screen_width, 3), (30, 30, 30), dtype=np.uint8)

        # Perform detection in both modes (so that Foreground Mask & Detection Overlay are meaningful)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        fgmask = fgbg.apply(blurred_frame)
        _, thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # For the detection overlay
        detection_display = frame.copy()
        cv2.drawContours(detection_display, contours, -1, (0, 0, 255), 2)

        # --- Resize camera frames for the 2x2 grid ---
        frame_resized = cv2.resize(frame, (cell_width, cell_height))
        fgmask_bgr = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
        fgmask_resized = cv2.resize(fgmask_bgr, (cell_width, cell_height))
        detection_resized = cv2.resize(detection_display, (cell_width, cell_height))

        # By default, let's keep the bottom-right cell black (or some neutral color)
        bottom_right_cell = np.zeros((cell_height, cell_width, 3), dtype=np.uint8)

        # ===========================
        # == CAMERA MODE (Demo) ====
        # ===========================
        if CAMERA_MODE:
            # 1) Title bar just says "Demo Mode"
            cv2.putText(title_bar, "Demo Mode", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 4, cv2.LINE_AA)

            # 2) 2×2 grid: top-left = camera, top-right = fgmask, bottom-left = detection overlay,
            #    bottom-right = black
            top_row = np.hstack([frame_resized, fgmask_resized])
            bottom_row = np.hstack([detection_resized, bottom_right_cell])
            grid = np.vstack([top_row, bottom_row])

            # Combine the title bar on top and the grid below
            combined_frame = np.vstack([title_bar, grid])

            # Show
            cv2.imshow("Game Window", combined_frame)

        # ===========================
        # == GAME MODE (RLGL)  =====
        # ===========================
        else:
            # If not in camera mode, we run the RLGL game
            # total_movement => sum of contour areas
            total_movement = sum(cv2.contourArea(c) for c in contours)

            # If the game is active, handle logic
            if game_active:
                # Preparation phase
                if game_state == "Preparation":
                    print("Preparation phase started.")
                    preparation_sound.play()
                    prep_start_time = time.time()

                    while time.time() - prep_start_time < PREPARATION_TIME:
                        # Countdown left
                        remaining_prep_time = PREPARATION_TIME - int(time.time() - prep_start_time)

                        # Show the 2×2 grid as black except maybe the camera feed if you prefer
                        black_panel = np.zeros((cell_height, cell_width, 3), dtype=np.uint8)
                        # Bottom-right cell can be a "waiting" grey
                        waiting_cell = np.full((cell_height, cell_width, 3), (50, 50, 50), dtype=np.uint8)

                        # Title bar showing "PREPARATION"
                        prep_title_bar = title_bar.copy()
                        cv2.putText(prep_title_bar, f"Preparation - Starting in {remaining_prep_time}s",
                                    (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                                    (255, 255, 255), 3, cv2.LINE_AA)

                        # Build the grid (camera feed optional; let's keep black for clarity)
                        top_row = np.hstack([black_panel, black_panel])
                        bottom_row = np.hstack([black_panel, waiting_cell])
                        grid = np.vstack([top_row, bottom_row])

                        prep_frame = np.vstack([prep_title_bar, grid])
                        cv2.imshow("Game Window", prep_frame)
                        if cv2.waitKey(1) & 0xFF == 27:
                            # ESC to exit early
                            cap.release()
                            cv2.destroyAllWindows()
                            return

                    # After preparation, switch to Green Light
                    print("Preparation phase over. Game starting!")
                    pygame.mixer.music.play()
                    game_state = "Green Light"
                    start_time = time.time()
                    last_state_change_time = time.time()

                # Time check
                elapsed_time = time.time() - start_time
                if (elapsed_time > GAME_TIMER) and not game_over:
                    print("Time is up! You lose.")
                    lose_sound.play()
                    game_over = True
                    game_state = "Idle"
                    game_active = False

                # RED / GREEN logic if not game_over
                if not game_over:
                    if game_state == "Red Light":
                        bottom_right_cell[:] = (0, 0, 255)  # Red
                        # If past grace period, movement => lose
                        if (time.time() - red_light_start_time > GRACE_RED) and (total_movement > DETECTION_AREA):
                            print("Movement detected! You lose.")
                            lose_sound.play()
                            game_over = True
                            game_state = "Idle"
                            game_active = False
                        # Switch back to green if we've been red for enough time
                        elif time.time() - last_state_change_time > RED_LIGHT_DURATION:
                            game_state = "Green Light"
                            pygame.mixer.music.play()
                            last_state_change_time = time.time()
                            print("GREEN LIGHT! You can move.")

                    elif game_state == "Green Light":
                        bottom_right_cell[:] = (0, 255, 0)  # Green
                        # Random switch to red
                        if (time.time() - last_state_change_time) > random.uniform(GREEN_LIGHT_MIN, GREEN_LIGHT_MAX):
                            game_state = "Red Light"
                            redlight_sound.play()
                            last_state_change_time = time.time()
                            red_light_start_time = time.time()
                            print("RED LIGHT! Stop moving.")

                # Update the title bar with game state & time
                # E.g. "State: Green Light | Time Left: XXs"
                # If game over, it will revert to "Idle" eventually, so you can reflect that up top as well
                title_str = f"State: {game_state} | Time Left: {max(0, GAME_TIMER - int(elapsed_time))}s"
                cv2.putText(title_bar, title_str, (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)

            else:
                # Game inactive (Idle or Over)
                # Title bar says either "Idle - Press R to Start" or "Game Over - Press R to Restart"
                if game_over:
                    title_text = "Game Over - Press R to Restart"
                else:
                    title_text = "Idle - Press R to Start"

                cv2.putText(title_bar, title_text, (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)

            # Build the final 2×2 grid in game mode
            top_row = np.hstack([frame_resized, fgmask_resized])
            bottom_row = np.hstack([detection_resized, bottom_right_cell])
            grid = np.vstack([top_row, bottom_row])

            # Combine the title bar + grid
            combined_frame = np.vstack([title_bar, grid])
            cv2.imshow("Game Window", combined_frame)

        # ===========================
        # ===== Key Handling ========
        # ===========================
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC to quit
            print("Exiting...")
            break

        if not CAMERA_MODE:
            # Only relevant if not in Demo mode
            if key == ord('r'):
                print("Starting (or Restarting) the game...")
                # Reset game variables
                game_active = True
                game_over = False
                game_state = "Preparation"

            elif key == ord(' '):
                # Force a win if in green light
                if game_active and (game_state == "Green Light") and not game_over:
                    print("You win! Congratulations!")
                    win_sound.play()
                    game_over = True
                    game_state = "Idle"
                    game_active = False

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

# ===========================
# ========= RUNNER ==========
# ===========================
if __name__ == "__main__":
    game_loop()
