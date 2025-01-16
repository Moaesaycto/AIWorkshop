import cv2
import numpy as np
import time
import pygame
import random

# Parameters
SENSITIVITY_THRESHOLD = 40
DETECTION_AREA = 2000
GAME_TIMER = 60
GREEN_LIGHT_MIN = 3
GREEN_LIGHT_MAX = 7
RED_LIGHT_DURATION = 5
GRACE_RED = 0.5
PREPARATION_TIME = 10  # Time to wait during the preparation phase (in seconds)

# Initialize Pygame for sound playback
pygame.mixer.init()
pygame.mixer.music.load('./assets/greenlight.mp3')
redlight_sound = pygame.mixer.Sound('./assets/redlight.mp3')
lose_sound = pygame.mixer.Sound('./assets/lose.mp3')
win_sound = pygame.mixer.Sound('./assets/win.mp3')
preparation_sound = pygame.mixer.Sound('./assets/preparation.mp3')  # Add a preparation sound

def game_loop():
    cap = cv2.VideoCapture(0)
    fgbg = cv2.createBackgroundSubtractorMOG2(history=5, varThreshold=SENSITIVITY_THRESHOLD)

    # --- Game State Variables ---
    game_active = False       # False => idle mode; True => actively playing
    game_over = False         # True once player loses or wins
    game_state = "Idle"       # "Idle", "Preparation", "Green Light", or "Red Light"

    start_time = 0
    last_state_change_time = 0
    red_light_start_time = 0

    print("Press 'R' to start the game.")

    while True:
        # If the game is active, run detection & update logic
        if game_active:
            # Handle preparation phase
            if game_state == "Preparation":
                print("Preparation phase started.")
                preparation_sound.play()  # Play preparation sound
                prep_start_time = time.time()
                
                # Display preparation message during the 10-second countdown
                while time.time() - prep_start_time < PREPARATION_TIME:
                    remaining_prep_time = PREPARATION_TIME - int(time.time() - prep_start_time)
                    prep_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(prep_frame, f"Get Ready! Starting in {remaining_prep_time}s",
                                (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.imshow('Game Frame', prep_frame)
                    cv2.waitKey(1)  # Refresh frame during countdown
                
                # After preparation, transition to "Green Light"
                print("Preparation phase over. Game starting!")
                pygame.mixer.music.play()  # Play Green Light sound
                game_state = "Green Light"
                start_time = time.time()
                last_state_change_time = time.time()

            # 1. Grab frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame. Exiting...")
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

            # 2. Background subtraction & movement detection
            fgmask = fgbg.apply(blurred_frame)
            _, thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            total_movement = sum(cv2.contourArea(c) for c in contours)

            # 3. Game Timer Check
            elapsed_time = time.time() - start_time
            if (elapsed_time > GAME_TIMER) and not game_over:
                print("Time is up! You lose.")
                lose_sound.play()
                game_over = True
                game_state = "Idle"
                game_active = False  # return to idle

            # 4. Update Red/Green Light logic only if we're still active and not over
            if not game_over:
                # Display info
                cv2.putText(frame, f"State: {game_state}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, 
                            (0, 255, 0) if game_state == "Green Light" else (0, 0, 255), 2)
                cv2.putText(frame, f"Time Left: {max(0, GAME_TIMER - int(elapsed_time))}", 
                            (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                if game_state == "Red Light":
                    # Past the grace period, any movement => lose
                    if (time.time() - red_light_start_time > GRACE_RED) and (total_movement > DETECTION_AREA):
                        print("Movement detected! You lose.")
                        lose_sound.play()
                        game_over = True
                        game_state = "Idle"
                        game_active = False

                    # Switch back to green after RED_LIGHT_DURATION
                    elif time.time() - last_state_change_time > RED_LIGHT_DURATION:
                        game_state = "Green Light"
                        pygame.mixer.music.play()
                        last_state_change_time = time.time()
                        print("GREEN LIGHT! You can move.")

                elif game_state == "Green Light":
                    # Random time for green => switch to red
                    if (time.time() - last_state_change_time) > random.uniform(GREEN_LIGHT_MIN, GREEN_LIGHT_MAX):
                        game_state = "Red Light"
                        redlight_sound.play()
                        last_state_change_time = time.time()
                        red_light_start_time = time.time()
                        print("RED LIGHT! Stop moving.")

            # Show frames
            cv2.imshow('Game Frame', frame)
            cv2.imshow('Foreground Mask', fgmask)
            detection_display = frame.copy()
            cv2.drawContours(detection_display, contours, -1, (0, 0, 255), 2)
            cv2.imshow('Detection Overlay', detection_display)

        else:
            # Idle mode: Display a simple “Press R to start” screen
            idle_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            message = "Press 'R' to Start" if not game_over else "Press 'R' to Restart"
            cv2.putText(idle_frame, message, (120, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Game Frame', idle_frame)
            cv2.imshow('Foreground Mask', idle_frame)
            cv2.imshow('Detection Overlay', idle_frame)

        # ---- Key Events ----
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            # Start (or restart) the game
            print("Starting (or Restarting) the game...")
            # Reinitialize variables
            game_active = True
            game_over = False
            game_state = "Preparation"  # Start in preparation phase

        elif key == 27:  # ESC => exit
            print("Exiting game...")
            break

        elif key == ord(' '):
            if game_active and (game_state == "Green Light") and not game_over:
                print("You win! Congratulations!")
                win_sound.play()
                game_over = True
                game_state = "Idle"
                game_active = False

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    game_loop()
