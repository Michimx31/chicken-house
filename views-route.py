import flet as ft
import time
import time
#import RPi.GPIO as GPIO
from flet import Container, ElevatedButton, Page, Row, colors, padding

name = "Chicken Gate Control"

# GPIO setup
MOTOR_PIN_OPEN = 17
MOTOR_PIN_CLOSE = 2
switch_open_pin = 27  # Magnetic switch for open position
switch_close_pin = 22  # Magnetic switch for close position

# Gate states 
gate_status = ""

#state machine
# gate control state
gate_open = False

#test mit state machine
gate_state = "Closed"
toggle_gate = False
auto_toggle_gate = False 

# Default open and close times (e.g., 6:00 AM for opening, 6:00 PM for closing)
open_hour = 7
open_minute = 45
close_hour = 18
close_minute = 0



# UI Elements 
#gate_status_text = ft.Text(value="Motor Status: Unknown")


#Gate status 
def get_gateState():
    global gate_open
    #if (GPIO.input(switch_open_pin) == GPIO.HIGH and GPIO.input(switch_close_pin) == GPIO.LOW):
    if gate_open == False: # kann zu -> if not gate_open:
        time.sleep(1) 
        gate_status = "Open"
        gate_open = True
        return gate_status
    #elif (GPIO.input(switch_open_pin) == GPIO.LOW and GPIO.input(switch_close_pin) == GPIO.HIGH):
    if gate_open == True: # kann zu else
        time.sleep(1)
        gate_status = "Closed" 
        gate_open = False 
        return gate_status
    else: 
        gate_status = "Unknown" 
        return gate_status

# Motor control functions
def open_motor():    
    get_gateState()
    while gate_open !=True:
        # set output to open the motor
        #GPIO.output(MOTOR_PIN_OPEN, GPIO.HIGH)
        time.sleep(0.5)        
    # set output to stop the motor
    #GPIO.output(MOTOR_PIN_OPEN, GPIO.LOW)
    
def close_motor():    
    while gate_open !=False:
        get_gateState()
        # set output to open the motor
        #GPIO.output(MOTOR_PIN_CLOSE, GPIO.HIGH)
        time.sleep(0.5)        
    # set output to stop the motor
    #GPIO.output(MOTOR_PIN_CLOSE, GPIO.LOW)    
    
    
    
    #state machine for the gate     
gate_state = get_gateState()

match gate_state:
    case "Closed":
        if (gate_state == "Closed" and toggle_gate) or (gate_state == "Closed" and auto_toggle_gate):
            #GPIO.output(MOTOR_PIN_OPEN, GPIO.HIGH)
            start_time = time.time()
            gate_state = "Opening"
    case "Opening":       
        # Wait until the door is fully open or 60 seconds timeout
        while gate_state == 'Opening':
            if (gate_state == "Opening" and (GPIO.input(switch_open_pin) == GPIO.LOW and GPIO.input(switch_close_pin) == GPIO.LOW)):
                #GPIO.output(MOTOR_PIN_OPEN, GPIO.HIGH)
                gate_state = "Opening"
            elif (gate_state == "Opening" and (GPIO.input(switch_open_pin) == GPIO.HIGH and GPIO.input(switch_close_pin) == GPIO.LOW)):
                #GPIO.output(MOTOR_PIN_OPEN, GPIO.LOW)
                gate_state = "Open"   
            elapsed_time = time.time() - start_time
            if elapsed_time > 60:
                gate_status_text = 'Error in Opening - Close Sensor:{switch_close_pin} and Open Sensor:{switch_open_pin} '
                gate_state = 'Error in Opening'
                break    
        
    case "Error in Opening":
        gate_status_text = 'Error in Opening - Close Sensor:{switch_close_pin} and Open Sensor:{switch_open_pin} '
    
    case "Open":
        gate_status_text = 'Open'
        if (gate_state == "Open" and toggle_gate) or (gate_state == "Open" and auto_toggle_gate):
            #GPIO.output(MOTOR_PIN_CLOSE, GPIO.HIGH)
            start_time = time.time()
            gate_state = "Closing"
    case "Closing":
        # Wait until the door is fully closed or 60 seconds timeout
        while gate_state == 'Closing':
            if (gate_state == "Closing" and (GPIO.input(switch_close_pin) == GPIO.LOW and GPIO.input(switch_close_pin) == GPIO.LOW)):
                #GPIO.output(MOTOR_PIN_CLOSE, GPIO.HIGH)
                gate_state = "Closing"
            elif (gate_state == "Closing" and (GPIO.input(switch_open_pin) == GPIO.LOW and GPIO.input(switch_close_pin) == GPIO.HIGH)):
                #GPIO.output(MOTOR_PIN_CLOSE, GPIO.LOW)
                gate_state = "Closed"   
            elapsed_time = time.time() - start_time
            if elapsed_time > 60:
                gate_status_text = 'Error in Closing - Close Sensor:{switch_close_pin} and Open Sensor:{switch_open_pin} '
                gate_state = 'Error in Closing'
                break 
        
    case "Error in Closing":
        gate_status_text = 'Error in Closing - Close Sensor:{switch_close_pin} and Open Sensor:{switch_open_pin} '
        
    case "Unknown":
        gate_status_text = 'Unknown Gate State - Close Sensor:{switch_close_pin} and Open Sensor:{switch_open_pin} '   
        
         



def main(page: ft.Page):
    
    def toggle_motor(e):
        if gate_open:
            toggle_gate = True
            close_motor()
            if gate_open == False:
                gate_status_text.value = "Motor Closed Manually"
                house_img.src = close_image
                button.icon = ft.icons.ARROW_CIRCLE_UP
        else:
            open_motor()
            if gate_open:
                gate_status_text.value = "Motor Opened Manually"
                house_img.src = open_image
                button.icon = ft.icons.ARROW_CIRCLE_DOWN        
        page.update()
    
    def save_time_settings(e):
        # to do - save time settings persistent on raspi
        try:
            open_hours = int(open_hour_dropdown.value)
            open_minutes = int(open_minute_dropdown.value)
            close_hours = int(close_hour_dropdown.value)
            close_minutes = int(close_minute_dropdown.value)
            
            global open_time, close_time
            open_time = open_hours * 3600 + open_minutes * 60
            close_time = close_hours * 3600 + close_minutes * 60

            saved_time_text = f"Saved new Settings - Open Time: {open_hours}h {open_minutes}m, Close Time: {close_hours}h {close_minutes}m"
            page.snack_bar = ft.SnackBar(ft.Text(saved_time_text))
            page.snack_bar.open = True
            page.update()
                
            

        except ValueError:
            status_text.value = "Invalid input! Please enter numeric values for hours and minutes."
            page.update()
            
    ## -- Create UI elements    
    # Manual UI Elements
    button = ft.Container(padding=padding.only(left=30),content=ft.ElevatedButton(text="Toggle Motor",icon=ft.icons.ARROW_CIRCLE_DOWN,on_click=toggle_motor))  
    gate_status_text = ft.Text(value="Unknown")      
    
    # Settings UI Elements
    # Create dropdown options for time input
    hour_options = [ft.dropdown.Option(str(i)) for i in range(24)]
    minute_options = [ft.dropdown.Option(str(i)) for i in range(60)]
    
    open_description = ft.Text(value="Set the time to open the motor:",theme_style=ft.TextThemeStyle.LABEL_MEDIUM)
    open_hour_dropdown = ft.Dropdown(label="Open Time (hours)", options=hour_options, value=str(open_hour),width=100)
    open_minute_dropdown = ft.Dropdown(label="Open Time (minutes)", options=minute_options, value=str(open_minute), width=100)     
    close_description = ft.Text(value="Set the time to close the motor:",theme_style=ft.TextThemeStyle.LABEL_MEDIUM)
    close_hour_dropdown = ft.Dropdown(label="Close Time (hours)", options=hour_options, value=close_hour,width=100)
    close_minute_dropdown = ft.Dropdown(label="Close Time (minutes)", options=minute_options, value=close_minute, width=100) 
    save_button = ft.ElevatedButton(text="Save Settings", on_click=save_time_settings)
    saved_time_text = ft.Text(value="")
    settings_headline = ft.Text(value="Settings",theme_style=ft.TextThemeStyle.TITLE_MEDIUM)
    open_settings_row = ft.Row([open_hour_dropdown, open_minute_dropdown])
    close_settings_row = ft.Row([close_hour_dropdown, close_minute_dropdown])
    status_text = ft.Text(value="")
    
    # Define the images
    close_image = f"/house_open.png"
    open_image= f"/house_closed.png"
    
    house_img = ft.Image(
        src=close_image,
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN,
    )
    
           
    # Define the content areas for different navigation items
    first_content = ft.Column(
        #image 
        #show actual state -> gate is open / closed / error
        #show actual time and planned time for opening or closing depending on the act status 
        [
        ft.Text("This is the first content")
        ],        
        alignment=ft.MainAxisAlignment.START,
        spacing=2,
        expand=True,
    ) 
    
    
    
    second_content = ft.Column(
        #[ft.Text("Manual Mode"),ft.ElevatedButton(text="Toggle Motor",icon=ft.icons.ARROW_CIRCLE_DOWN,on_click=toggle_motor)],
        [
        ft.Text("Manual Mode"), 
        house_img,
        button,
        gate_status_text
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=2,
        expand=True,
    )
    
    settings_content = ft.Column(
        [settings_headline,
         open_description,
         open_settings_row,
         close_description,
         close_settings_row,
         save_button,
         saved_time_text,
         ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
        expand=True,
    )
    
    live_content = ft.Column(
        [ft.Text("This is the live content")],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
    )

    # Function to update content based on the selected index
    def update_content(selected_index):
        if selected_index == 0:
            content_container.controls = [first_content]
        elif selected_index == 1:
            content_container.controls = [second_content]
        elif selected_index == 2:
            content_container.controls = [settings_content]
        elif selected_index == 3:
            content_container.controls = [live_content]    
        page.update()

    # Create a container to hold the dynamic content
    content_container = ft.Column([], alignment=ft.MainAxisAlignment.START, expand=True)
    
    # Initialize with the first content
    update_content(0)
    
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=50,
        min_extended_width=350,
        
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.INFO, selected_icon=ft.icons.INFO, label="Home"
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.ARROW_CIRCLE_DOWN),
                selected_icon_content=ft.Icon(ft.icons.ARROW_CIRCLE_UP),
                label="Manual",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                label_content=ft.Text("Settings"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.CAMERA,
                selected_icon_content=ft.Icon(ft.icons.CAMERA),
                label_content=ft.Text("Live"),
            ),
        ],
        on_change=lambda e: update_content(e.control.selected_index),
    )

    # Layout with navigation rail and content area
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_container,
            ],
            width=400,
            height=400,
        )
    )

# Start the Flet app
ft.app(target=main)
