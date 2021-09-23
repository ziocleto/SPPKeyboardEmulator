# Importing stuff
import math
import pygame
import keyboard
import numpy
import vgamepad as vg
import whratio
from ctypes import windll
import win32api
import win32con
import win32gui
import pyautogui

################ INITIALISATION - LIBRARIES, WINDOW CALCULATIONS 
    
# Initialise Libraries
pygame.init()
gamepad = vg.VX360Gamepad()
screen_info = pygame.display.Info()

# Setting colours to be used
red = (255, 0, 0)
white = (255, 255, 255)
storror = (4, 245, 204)

# Calculate middle of monitor as integer
monitor_centreX = int(screen_info.current_w/2)
monitor_centreY = int(screen_info.current_h/2)

# Screen, Resolution Calculations & Remaining On Top 
    # Calculate the screen aspect ratio and split into 2 values
aspect1 = whratio.as_int(screen_info.current_w, screen_info.current_h)[0]
aspect2 = whratio.as_int(screen_info.current_w, screen_info.current_h)[1]

    # Use aspect ratio to create a small square window
window_width = int(aspect2 * screen_info.current_w / 100)
window_height = int(aspect1 * screen_info.current_h / 100)

    # Set window location as percentage of monitor to place in lower right quadrant
window_posX = int((screen_info.current_w/100)*75)
window_posY = int((screen_info.current_h/100)*75)

    # Create User32 variable for window
SetWindowPos = windll.user32.SetWindowPos

    # Create window for pygame using the calculations above
screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
black = (0, 0, 0)  # Transparency colour

    # Create layered window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    # Set window transparency color
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*black), 0, win32con.LWA_COLORKEY)

    # Keep window always on top and move to lower right quadrant
win32gui.SetWindowPos(hwnd, -1, window_posX, window_posY, 0, 0, 0x0001)

    # Calculate centre of pygame window
screen_centreX = window_width / 2
screen_centreY = window_height / 2


# INITIALISATION --- TEMPORARY VARIABLES 

initial_posX = 0  # PosX of mouse upon left click
initial_posY = 0  # PosY of mouse upon left click
joystick_area_radius = (window_height / 2.1)  # Radius of area representing joystick movement
python_loaded = 0  # Check initial loading of script
should_mouse_stick = 0  # Used to separate "run once" from "run continuously" functions in joystick input
trigger_delay = 0  # Used to create a time delay between resetting joystick and releasing right trigger
restart_delay = 0  # Used to create delays in the restart level command
joystick_marker_size = 10  # Radius of joystick tracking dot in the UI
joystick_marker_size_double = joystick_marker_size * 2  # Ensure the joystick marker stays inside the red circle
free_mouse_timer = 0
f_timer = 0  # Time delay used for releasing the f button
e_timer = 0  # Time delay used for releasing the e button
LCTRL_timer = 0  # Time delay used for releasing the LCTRL button
LShift_timer = 0  # Time delay used for releasing the LShift button
lock_mouse_to_centre = 1  # 0 = False, 1 = True
unfocus_emulator = 0  # 0 = False, 1 = True
forward_float = 0
sideways_float = 0
w_timer = 0
s_timer = 0
a_timer = 0
d_timer = 0
space_timer = 0
right_joystick_X_value = 0
right_joystick_Y_value = 0


############# FUNCTIONS FOR GAMEPAD INPUT 


    # Pulls Right Trigger
def right_trigger_pull():
    gamepad.right_trigger_float(value_float=1)


    # Moves Right Joystick
def right_joystick_movement():
    gamepad.right_joystick_float(x_value_float=mouse_movement_array_clipped[0],
                                 y_value_float=mouse_movement_array_clipped[1])


    # Resets Right Joystick to Zero
def right_joystick_reset():
    gamepad.right_joystick_float(x_value_float=0, y_value_float=0)


def left_joystick_movement():
    gamepad.left_joystick_float(x_value_float=numpy.clip(sideways_float, -1, 1),
                                y_value_float=numpy.clip(forward_float, -1, 1))


################################ PRIMARY LOGIC LOOP: While true loop to keep everything running
while True:

    ##### CHECKS/RESETS - GAME CLOSE, RESET DRAW
    # Check for ESC key pressed - Quit if so.

    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.QUIT:
            pygame.quit()
            break

# Redraw screen - clears previous mouse trails.
    screen.fill(0)

##### GATHER MOUSE DATA, CALCULATE NEEDED VALUES

    # Get mouse position X and Y on movement
    current_posX = pyautogui.position()[0]
    current_posY = pyautogui.position()[1]

    # Get mouse has distance moved in X and Y from LMB
    mouse_posX_difference = min(current_posX-initial_posX, joystick_area_radius)
    mouse_posY_difference = min(current_posY-initial_posY, joystick_area_radius)


    # Calculate the angle from centre of joystick area to the edge (or overshoot) at which the mouse currently is
    mouse_clamp_angle = numpy.arctan2(mouse_posY_difference, mouse_posX_difference)

    # Limiting the joystick input values between -1 and 1 (Any more and vgamepad won't accept the input)
    X_axis_movement = mouse_posX_difference/joystick_area_radius
    Y_axis_movement = (mouse_posY_difference/joystick_area_radius)*-1

    # Clips mouse position value to the joystick to -1 and 1 to prevent joystick looping back to opposite side
    mouse_movement_array = numpy.array([X_axis_movement, Y_axis_movement])
    mouse_movement_array_clipped = numpy.clip(mouse_movement_array, -1, 1)

    # Traces out from joystick centre at the clamp angle determined above, to the edge of the joystick area
    mouse_clamp_posX = screen_centreX + (
                (joystick_area_radius - joystick_marker_size_double) * numpy.cos(mouse_clamp_angle))
    mouse_clamp_posY = screen_centreY + (
                (joystick_area_radius - joystick_marker_size_double) * numpy.sin(mouse_clamp_angle))

    # Logic for mouse controlling camera when RMB is pressed
    if python_loaded == 0:
        pyautogui.moveTo(monitor_centreX, monitor_centreY)
        initial_posX = pyautogui.position()[0]
        initial_posY = pyautogui.position()[1]
        python_loaded = 1
    else:
        if win32api.GetKeyState(win32con.VK_RBUTTON) < 0 and unfocus_emulator == 0:
            right_joystick_movement()
            lock_mouse_to_centre = True
        else:
            right_joystick_reset()

    if unfocus_emulator == 0 and lock_mouse_to_centre:
        if abs(math.hypot(current_posX - monitor_centreX, current_posY - monitor_centreY)) > 10:
            pyautogui.moveTo(monitor_centreX, monitor_centreY)  # This line pulls the mouse back to monitor's centre

####### Main Behaviour Loop - Mouse is Pressed. 
    if win32api.GetKeyState(win32con.VK_LBUTTON) < 0 and unfocus_emulator == 0:

        trigger_delay = 200  # Set/Reset a delay for releasing trigger. Used later.

        ######### When Mouse is FIRST pressed, set an initial position.
        if should_mouse_stick == 0:
            initial_posX = pyautogui.position()[0]
            initial_posY = pyautogui.position()[1]
            should_mouse_stick = 1
            lock_mouse_to_centre = False

        #########  While mouse is being held down, main logic for Mouse/Vault Control.
        if should_mouse_stick == 1:

            # Draw the static outer circle.
            pygame.draw.circle(screen, red, (screen_centreX, screen_centreY), joystick_area_radius,
                               joystick_marker_size)

            # Calculate the mouse distance from start point.
            distance_from_centre = abs(math.hypot(current_posX - initial_posX, current_posY - initial_posY))

            # If the LMB is pressed (not RMB) pull the trigger to vault (not camera)
            right_trigger_pull()
            gamepad.update()


            # Drawing the blue dot at the position of the mouse.
            if distance_from_centre < joystick_area_radius-joystick_marker_size_double:
                pygame.draw.circle(screen, white,
                               (screen_centreX + mouse_posX_difference, screen_centreY + mouse_posY_difference),
                               joystick_marker_size)

            # If distance_from_centre > joystick_area_radius-joystick_marker_size_double:
            else:
                pygame.draw.circle(screen, storror, (mouse_clamp_posX, mouse_clamp_posY), joystick_marker_size)

        # Finally, move right joystick and update gamepad.
        right_joystick_movement()
        gamepad.update()

        

######## Reset - Mouse is Released 
    else:

        # Handler to turn off right trigger, if the delay timer is over. Or, decrease it otherwise.
        if trigger_delay == 1:
            gamepad.right_trigger_float(value_float=0)
            trigger_delay = 0

        if trigger_delay > 1:

            # NOTE: I MADE IT CONTINUE TO DRAW THE CIRCLE WHILE THE DELAY IS ON, TO GIVE SOME VISUAL FEEDBACK.
            right_joystick_reset()
            pygame.draw.circle(screen, red, (screen_centreX, screen_centreY), joystick_area_radius,
                               joystick_marker_size)
            pygame.draw.circle(screen, white,
                               (screen_centreX, screen_centreY),
                               joystick_marker_size)
            trigger_delay -= 1
            lock_mouse_to_centre = True


        ## Reset variable for first mouse press initialisation.
        should_mouse_stick = 0
        gamepad.update()

######################### OTHER BUTTONS FOR PC CONTROL 

    # Emulates f as right joystick
    if win32api.GetKeyState(70) < 0 and unfocus_emulator == 0:  # 70 is ASCII for 'F'
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
        f_timer = 10
    if f_timer > 0:
        f_timer -= 1
    if f_timer == 1:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
        f_timer = 0


    # Emulates shift as left trigger
    if win32api.GetKeyState(win32con.VK_LSHIFT) < 0 and unfocus_emulator == 0:
        gamepad.left_trigger_float(value_float=1)
        LShift_timer = 10
    if LShift_timer > 0:
        LShift_timer -= 1
    if LShift_timer == 1:
        gamepad.left_trigger_float(value_float=0)
        LShift_timer = 0

    # Emulates ctrl as left bumper
    if win32api.GetKeyState(win32con.VK_LCONTROL) < 0 and unfocus_emulator == 0:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        LCTRL_timer = 10
    if LCTRL_timer > 0:
        LCTRL_timer -= 1
    if LCTRL_timer == 1:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        LCTRL_timer = 0

    # Camera toggle
    if win32api.GetKeyState(69) < 0 and unfocus_emulator == 0:  # 69 is ASCII for 'E'... Noice
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        e_timer = 10
    if e_timer > 0:
        e_timer -= 1
    if e_timer == 1:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        e_timer = 0

    # Restart level
    if keyboard.is_pressed('r') and restart_delay == 0 and unfocus_emulator == 0:
        keyboard.send('`')
        restart_delay = 1
        if restart_delay == 1:  # I know this is a stupid way of doing this but keyboard.write was having a hissy fit
            keyboard.send('r')
            keyboard.send('e')
            keyboard.send('s')
            keyboard.send('t')
            keyboard.send('tab')
            keyboard.send('enter')

    # If ESC is pressed, close the emulator
    if win32api.GetKeyState(win32con.VK_ESCAPE) < 0:
        pygame.quit()
        break

    # Logic for focusing/unfocusing the emulator
    if free_mouse_timer > 0:
        free_mouse_timer -= 1

    if free_mouse_timer == 0:
        if keyboard.is_pressed('alt'):
            unfocus_emulator = (unfocus_emulator + 1) % 2
            free_mouse_timer = 1000
    print(unfocus_emulator)

    # Better WASD controls
    if keyboard.is_pressed('w') and unfocus_emulator == 0:
        forward_float += 0.01
        w_timer = 10
    if w_timer > 0:
        w_timer -= 1
    if w_timer == 1:
        if forward_float > 0:
            forward_float = 0
            w_timer = 0

    if keyboard.is_pressed('s') and unfocus_emulator == 0:
        forward_float -= 0.01
        s_timer = 10
    if s_timer > 0:
        s_timer -= 1
    if s_timer == 1:
        forward_float = 0
        s_timer = 0

    if keyboard.is_pressed('a') and unfocus_emulator == 0:
        sideways_float -= 0.01
        a_timer = 10
    if a_timer > 0:
        a_timer -= 1
    if a_timer == 1:
        sideways_float = 0
        a_timer = 0

    if keyboard.is_pressed('d') and unfocus_emulator == 0:
        sideways_float += 0.01
        d_timer = 10
    if d_timer > 0:
        d_timer -= 1
    if d_timer == 1:
        sideways_float = 0
        d_timer = 0

    left_joystick_movement()

    if keyboard.is_pressed('space') and unfocus_emulator == 0:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        space_timer = 10
    if space_timer > 0:
        space_timer -= 1
    if space_timer == 1:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        space_timer = 0
######################### UPDATING DISPLAY 

    pygame.display.update()
    gamepad.update()
