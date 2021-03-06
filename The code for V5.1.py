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
myfont = pygame.font.SysFont('Calibri', 22)

# Setting colours to be used
crimson = (220, 20, 60)
emerald = (27, 121, 49)
white = (255, 255, 255)
storror = (4, 245, 204)
menu_bg = (11, 61, 53)

# Calculate middle of monitor as integer
monitor_centreX = int(screen_info.current_w/2)
monitor_centreY = int(screen_info.current_h/2)

ScreenWidthTESTING = screen_info.current_w
ScreenHeightTESTING = screen_info.current_h

# Screen, Resolution Calculations & Remaining On Top
    # Calculate the screen aspect ratio and split into 2 values
aspect1 = whratio.as_int(ScreenWidthTESTING, ScreenHeightTESTING)[0]
aspect2 = whratio.as_int(ScreenWidthTESTING, ScreenHeightTESTING)[1]

MonitorWidthMultiplier = ScreenWidthTESTING * 0.01
MonitorHeightMultiplier = ScreenHeightTESTING * 0.01
PygameWindowClip = min(int(ScreenWidthTESTING * 0.2), int(ScreenHeightTESTING * 0.2))

    # Use aspect ratio to create a small square window
window_width = int(numpy.clip(aspect2 * MonitorWidthMultiplier, 0, PygameWindowClip))  # Pygame window width
window_height = int(numpy.clip(aspect1 * MonitorHeightMultiplier, 0, PygameWindowClip))  # Pygame window height

    # Set window location as percentage of monitor to place in lower right quadrant
window_posX = int((screen_info.current_w/100)*60)
window_posY = int((screen_info.current_h/100)*40)

    # Create User32 variable for window
SetWindowPos = windll.user32.SetWindowPos

    # Create window for pygame using the calculations above
screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
black = (0, 0, 0)  # Transparency colour

    # Create text surface
Command1 = "RestartLevel"
Command2 = "ToggleDebugCamera"
Command3 = "Teleport"
Command4 = "FOV 120"
commandcolour1 = white
commandcolour2 = white
commandcolour3 = white
commandcolour4 = white
Command1Surface = myfont.render(Command1, True, (commandcolour1))
Command2Surface = myfont.render(Command2, True, (commandcolour2))
Command3Surface = myfont.render(Command3, True, (commandcolour3))
Command4Surface = myfont.render(Command4, True, (commandcolour4))

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
right_joystick_X_value = 0
right_joystick_Y_value = 0
python_loaded = 0  # Check initial loading of script
should_mouse_stickL = 0  # Used to separate "run once" from "run continuously" functions for LMB
should_mouse_stickR = 0  # Used to separate "run once" from "run continuously" functions for RMB
trigger_delay = 0  # Used to create a time delay between resetting joystick and releasing right trigger
restart_delay = 0  # Used to create delays in the restart level command
joystick_area_radius = (window_height / 2.1)  # Radius of area representing joystick movement
joystick_marker_size = 8  # Radius of joystick tracking dot in the UI
joystick_marker_size_double = joystick_marker_size * 2  # Ensure the joystick marker stays inside the red circle
free_mouse_timer = 0
f_timer = 0  # Time delay used for releasing the f button
e_timer = 0  # Time delay used for releasing the e button
LCTRL_timer = 0  # Time delay used for releasing the LCTRL button
LShift_timer = 0  # Time delay used for releasing the LShift button
lock_mouse_to_centre = True
unfocus_emulator = 0  # 0 = False, 1 = True
forward_float = 0
sideways_float = 0
w_timer = 0
s_timer = 0
a_timer = 0
d_timer = 0
space_timer = 0
vault_sensitivity = 0.004
position_timer = 0
current_posX = 0
current_posY = 0
mouse_posX_difference = 0
mouse_posY_difference = 0
alt_pressed = 0
is_outline_red = 0
num1_timer = 0
num2_pressed = 0
HUD = 0
CommandMenuOpen = 0
CommandSelected = 0
menu_cooldown = 0
select_command = 0
enter_timer = 0
RB_timer = 0

############# FUNCTIONS FOR GAMEPAD INPUT


    # Pulls Right Trigger
def right_trigger_pull():
    gamepad.right_trigger_float(value_float=1)


def right_trigger_reset():
    gamepad.right_trigger_float(value_float=0)


    # Moves Right Joystick
def right_joystick_movement():
    gamepad.right_joystick_float(x_value_float=numpy.clip(right_joystick_X_value, -0.99, 0.99),
                                 y_value_float=numpy.clip(right_joystick_Y_value, -0.99, 0.99))


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

##### GATHER MOUSE DATA, CALCULATE NEEDED VALUES

    joystick_marker_posX = screen_centreX + (joystick_area_radius * right_joystick_X_value)
    joystick_marker_posY = screen_centreY + (joystick_area_radius * right_joystick_Y_value) * -1

    # Joystick marker angle
    joystick_marker_minX = min(joystick_marker_posX - screen_centreX, joystick_area_radius)
    joystick_marker_minY = min(joystick_marker_posY - screen_centreY, joystick_area_radius)
    joystick_angle = numpy.arctan2(joystick_marker_minY, joystick_marker_minX)

    # Joystick marker distance from centre
    distance_from_centre = abs(math.hypot(joystick_marker_posX - screen_centreX, joystick_marker_posY - screen_centreY))

    # Mouse distance from centre of joystick area
    mouse_distance_from_centre = abs(math.hypot(pyautogui.position()[0] - (window_posX + screen_centreX),
                                                pyautogui.position()[1] - (window_posY + screen_centreY)))

    # Joystick marker clamped positions
    joystick_marker_clampedX = screen_centreX + (
                (joystick_area_radius - joystick_marker_size_double) * numpy.cos(joystick_angle))
    joystick_marker_clampedY = screen_centreY + (
            (joystick_area_radius - joystick_marker_size_double) * numpy.sin(joystick_angle))


    # Centre mouse in joystick area upon loading the script (Just tidies everything up by starting in the middle)
    if python_loaded == 0:
        pyautogui.moveTo(window_posX + screen_centreX, window_posY + screen_centreY)
        initial_posX = pyautogui.position()[0]
        initial_posY = pyautogui.position()[1]
        python_loaded = 1

    # If mouse gets too far from starting position, reset it. (Basically giving you infinite screen space)
    if mouse_distance_from_centre > 0 and win32api.GetKeyState(win32con.VK_LBUTTON) > -1 and win32api.GetKeyState(win32con.VK_RBUTTON) > -1 and unfocus_emulator == 0:
        pyautogui.moveTo(window_posX + screen_centreX, window_posY + screen_centreY)

    # Logic for mouse controlling camera when RMB is pressed
    if win32api.GetKeyState(win32con.VK_RBUTTON) < 0 and unfocus_emulator == 0:
        if should_mouse_stickR == 0:
            pyautogui.moveTo(window_posX + screen_centreX, window_posY + screen_centreY)
            should_mouse_stickR = 1

        if should_mouse_stickR == 1:
            # Whilst mouse is held down find distance travelled every 5 ticks
            if position_timer == 0:
                initial_posX = pyautogui.position()[0]
                initial_posY = pyautogui.position()[1]
                position_timer = 5
            if position_timer > 1:
                position_timer -= 1
            if position_timer == 1:
                current_posX = pyautogui.position()[0]
                current_posY = pyautogui.position()[1]
                mouse_posX_difference = current_posX - initial_posX
                mouse_posY_difference = current_posY - initial_posY
                position_timer = 0

            # Whilst RMB is held down, control Right Joystick, and do the mouse movement math
            right_joystick_movement()
            if mouse_posX_difference > 0 and right_joystick_X_value < 1:
                right_joystick_X_value += abs(mouse_posX_difference) * vault_sensitivity
            if mouse_posX_difference < 0 and right_joystick_X_value > -1:
                right_joystick_X_value -= abs(mouse_posX_difference) * vault_sensitivity
            if mouse_posY_difference < 0 and right_joystick_Y_value < 1:
                right_joystick_Y_value += abs(mouse_posY_difference) * vault_sensitivity
            if mouse_posY_difference > 0 and right_joystick_Y_value > -1:
                right_joystick_Y_value -= abs(mouse_posY_difference) * vault_sensitivity
            gamepad.update()
    else:
        right_joystick_reset()
        should_mouse_stickR = 0

####### Main Behaviour Loop - Mouse is Pressed.
    if win32api.GetKeyState(win32con.VK_LBUTTON) < 0 and unfocus_emulator == 0:

        if should_mouse_stickL == 0:
            trigger_delay = 50  # Set/Reset a delay for releasing trigger. Used later.
            pyautogui.moveTo(window_posX + screen_centreX, window_posY + screen_centreY)
            should_mouse_stickL = 1

        if should_mouse_stickL == 1:
            # Whilst mouse is held down find distance travelled every 5 ticks
            if position_timer == 0:
                initial_posX = pyautogui.position()[0]
                initial_posY = pyautogui.position()[1]
                position_timer = 5
            if position_timer > 1:
                position_timer -= 1
            if position_timer == 1:
                current_posX = pyautogui.position()[0]
                current_posY = pyautogui.position()[1]
                mouse_posX_difference = current_posX - initial_posX
                mouse_posY_difference = current_posY - initial_posY
                position_timer = 0

            # Whilst LMB is held down, pull RT, control Right Joystick, and do the mouse movement math
            right_trigger_pull()
            right_joystick_movement()
            if mouse_posX_difference > 0 and right_joystick_X_value < 1:
                right_joystick_X_value += abs(mouse_posX_difference) * vault_sensitivity
            if mouse_posX_difference < 0 and right_joystick_X_value > -1:
                right_joystick_X_value -= abs(mouse_posX_difference) * vault_sensitivity
            if mouse_posY_difference < 0 and right_joystick_Y_value < 1:
                right_joystick_Y_value += abs(mouse_posY_difference) * vault_sensitivity
            if mouse_posY_difference > 0 and right_joystick_Y_value > -1:
                right_joystick_Y_value -= abs(mouse_posY_difference) * vault_sensitivity
            gamepad.update()


            # Draw the joystick HUD based on position of the marker
            if unfocus_emulator == 0 and HUD == 0:
                if distance_from_centre < joystick_area_radius - joystick_marker_size_double:
                    screen.fill(0)
                    pygame.draw.circle(screen, crimson, (screen_centreX, screen_centreY), joystick_area_radius,
                                       joystick_marker_size)
                    pygame.draw.circle(screen, white, (joystick_marker_posX, joystick_marker_posY),
                                       joystick_marker_size)
                    is_outline_red = 1
                else:
                    pygame.draw.circle(screen, storror, (screen_centreX, screen_centreY), joystick_area_radius,
                                       joystick_marker_size)
                    pygame.draw.circle(screen, white, (joystick_marker_clampedX, joystick_marker_clampedY),
                                       joystick_marker_size)
                    is_outline_red = 0

    # When LMB is released, reset everything
    else:

        # Handler to turn off right trigger, if the delay timer is over. Or, decrease it otherwise
        if trigger_delay == 1:
            right_trigger_reset()
            trigger_delay = 0
            screen.fill(0)

        # Reset joystick and all associated values, ready for next usage
        if trigger_delay > 1:
            right_joystick_reset()
            # Continue drawing HUD whilst the delay is on, for feedback sake
            if HUD == 0:
                if distance_from_centre < joystick_area_radius - joystick_marker_size_double:
                    if is_outline_red == 1:
                        pygame.draw.circle(screen, crimson, (screen_centreX, screen_centreY), joystick_area_radius,
                                           joystick_marker_size)
                    else:
                        pygame.draw.circle(screen, storror, (screen_centreX, screen_centreY), joystick_area_radius,
                                           joystick_marker_size)
                else:
                    pygame.draw.circle(screen, storror, (screen_centreX, screen_centreY), joystick_area_radius,
                                       joystick_marker_size)
                    pygame.draw.circle(screen, white, (joystick_marker_clampedX, joystick_marker_clampedY),
                                       joystick_marker_size)

            right_joystick_X_value = 0
            right_joystick_Y_value = 0
            trigger_delay -= 1
            initial_posX = pyautogui.position()[0]
            initial_posY = pyautogui.position()[1]
            should_mouse_stickL = 0

    # Reset variable for first mouse press, and update the gamepad
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

    ############ If tab is pressed, open menu of commands and cycle through them

    if menu_cooldown > 0:
        menu_cooldown -= 1

    ###### Open the menu
    if keyboard.is_pressed('tab') and unfocus_emulator == 0 and menu_cooldown == 0 and CommandMenuOpen == 0:
        commandcolour1 = crimson
        screen.fill(menu_bg)
        screen.blit(Command1Surface, (0,10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit(Command4Surface, (0, 160))
        CommandMenuOpen = 1
        CommandSelected = 0
        menu_cooldown = 120

    ##### Close the menu
    if keyboard.is_pressed('tab') and unfocus_emulator == 0 and menu_cooldown == 0 and CommandMenuOpen == 1:
        screen.fill(0)
        menu_cooldown = 120
        CommandMenuOpen = 0

    ### Cycling down the menu
    if keyboard.is_pressed('down') and CommandSelected == 0 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour1 = storror
        screen.blit((myfont.render(Command1, True, (commandcolour1))), (0, 10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit(Command4Surface, (0, 160))
        CommandSelected = 1
        menu_cooldown = 120

    if keyboard.is_pressed('down') and CommandSelected == 1 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour1 = white
        commandcolour2 = storror
        screen.blit(Command1Surface, (0, 10))
        screen.blit((myfont.render(Command2, True, (commandcolour2))), (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit(Command4Surface, (0, 160))
        CommandSelected = 2
        menu_cooldown = 120

    if keyboard.is_pressed('down') and CommandSelected == 2 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour2 = white
        commandcolour3 = storror
        screen.blit(Command1Surface, (0, 10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit((myfont.render(Command3, True, (commandcolour3))), (0, 110))
        screen.blit(Command4Surface, (0, 160))
        CommandSelected = 3
        menu_cooldown = 120

    if keyboard.is_pressed('down') and CommandSelected == 3 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour3 = white
        commandcolour4 = storror
        screen.blit(Command1Surface, (0, 10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit((myfont.render(Command4, True, (commandcolour4))), (0, 160))
        CommandSelected = 4
        menu_cooldown = 120

    if keyboard.is_pressed('down') and CommandSelected == 4 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour4 = white
        commandcolour1 = storror
        screen.blit((myfont.render(Command1, True, (commandcolour1))), (0, 10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit(Command4Surface, (0, 160))
        CommandSelected = 1
        menu_cooldown = 120

    ### Cycling up the menu
    if keyboard.is_pressed('up') and CommandSelected == 0 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour4 = storror
        screen.blit(Command1Surface, (0, 10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit((myfont.render(Command4, True, (commandcolour4))), (0, 160))
        CommandSelected = 4
        menu_cooldown = 120

    if keyboard.is_pressed('up') and CommandSelected == 1 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour4 = storror
        screen.blit(Command1Surface, (0, 10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit((myfont.render(Command4, True, (commandcolour4))), (0, 160))
        CommandSelected = 4
        menu_cooldown = 120

    if keyboard.is_pressed('up') and CommandSelected == 2 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour2 = white
        commandcolour1 = storror
        screen.blit((myfont.render(Command1, True, (commandcolour1))), (0, 10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit(Command4Surface, (0, 160))
        CommandSelected = 1
        menu_cooldown = 120

    if keyboard.is_pressed('up') and CommandSelected == 3 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour3 = white
        commandcolour2 = storror
        screen.blit(Command1Surface, (0, 10))
        screen.blit((myfont.render(Command2, True, (commandcolour2))), (0, 60))
        screen.blit(Command3Surface, (0, 110))
        screen.blit(Command4Surface, (0, 160))
        CommandSelected = 2
        menu_cooldown = 120

    if keyboard.is_pressed('up') and CommandSelected == 4 and menu_cooldown == 0:
        screen.fill(menu_bg)
        commandcolour4 = white
        commandcolour3 = storror
        screen.blit(Command1Surface, (0, 10))
        screen.blit(Command2Surface, (0, 60))
        screen.blit((myfont.render(Command3, True, (commandcolour3))), (0, 110))
        screen.blit(Command4Surface, (0, 160))
        CommandSelected = 3
        menu_cooldown = 120

    ### Selecting a command

    if keyboard.is_pressed('enter') and CommandMenuOpen == 1:
        screen.fill(0)
        enter_timer = 10
    if enter_timer > 0:
        enter_timer -= 1
    if enter_timer == 1 and CommandSelected == 1:
        pyautogui.typewrite(['`', 'r', 'e', 's', 'tab', 'enter'], interval=.05)
        enter_timer = 0
    if enter_timer == 1 and CommandSelected == 2:
        pyautogui.typewrite(['`', 't', 'o', 'g', 'g', 'l', 'e', 'd', 'tab', 'enter'], interval=.05)
        enter_timer = 0
    if enter_timer == 1 and CommandSelected == 3:
        pyautogui.typewrite(['`', 't', 'e', 'l', 'e', 'p', 'o', 'r', 't', 'enter'], interval=.05)
        enter_timer = 0
    if enter_timer == 1 and CommandSelected == 4:
        pyautogui.typewrite(['`', 'f', 'o', 'v', 'space', '1', '2', '0', 'enter'], interval=.05)
        enter_timer = 0

############## Extra controls

    # If ESC is pressed, close the emulator
    if win32api.GetKeyState(win32con.VK_ESCAPE) < 0:
        pygame.quit()
        break

    # Logic for focusing/unfocusing the emulator
    if free_mouse_timer > 0:
        free_mouse_timer -= 1

    if free_mouse_timer == 0:
        if keyboard.is_pressed('alt'):
            alt_pressed = 1
        if not keyboard.is_pressed('alt') and alt_pressed == 1:
            unfocus_emulator = (unfocus_emulator + 1) % 2
            free_mouse_timer = 10
            alt_pressed = 0

    # Better WASD controls
    if keyboard.is_pressed('w') and unfocus_emulator == 0:
        forward_float += 0.01
        w_timer = 10
    if w_timer > 1:
        w_timer -= 1
    if w_timer == 1:
        if forward_float > 0:
            forward_float -= 0.05

    if keyboard.is_pressed('s') and unfocus_emulator == 0:
        forward_float -= 0.01
        s_timer = 10
    if s_timer > 1:
        s_timer -= 1
    if s_timer == 1:
        if forward_float < 0:
            forward_float += 0.05

    if keyboard.is_pressed('a') and unfocus_emulator == 0:
        sideways_float -= 0.01
        a_timer = 10
    if a_timer > 1:
        a_timer -= 1
    if a_timer == 1:
        if sideways_float < 0:
            sideways_float += 0.05

    if keyboard.is_pressed('d') and unfocus_emulator == 0:
        sideways_float += 0.01
        d_timer = 10
    if d_timer > 1:
        d_timer -= 1
    if d_timer == 1:
        if sideways_float > 0:
            sideways_float = 0.05

    left_joystick_movement()

    if win32api.GetKeyState(win32con.VK_MBUTTON) < 0 and unfocus_emulator == 0:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        RB_timer = 10
    if RB_timer > 1:
        RB_timer -= 1
    if RB_timer == 1:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        RB_timer = 0

    if keyboard.is_pressed('v') and unfocus_emulator == 0:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        space_timer = 10
    if space_timer > 0:
        space_timer -= 1
    if space_timer == 1:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        space_timer = 0

    if keyboard.is_pressed('6'):
        num2_pressed = 1
    if not keyboard.is_pressed('0') and num2_pressed == 1:
        HUD = (HUD + 1) % 2
        num2_pressed = 0

######################### UPDATING DISPLAY

    pygame.display.update()
    gamepad.update()
