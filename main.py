import time
import flet as ft
#import RPi.GPIO as GPIO

# GPIO setup
MOTOR_PIN_OPEN = 17
MOTOR_PIN_CLOSE = 27

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(MOTOR_PIN_OPEN, GPIO.OUT)
#GPIO.setup(MOTOR_PIN_CLOSE, GPIO.OUT)

# Motor control functions
def open_motor():
    #GPIO.output(MOTOR_PIN_OPEN, GPIO.HIGH)
    time.sleep(1)  # Adjust this duration for your motor
    #GPIO.output(MOTOR_PIN_OPEN, GPIO.LOW)

def close_motor():
    #GPIO.output(MOTOR_PIN_CLOSE, GPIO.HIGH)
    time.sleep(1)  # Adjust this duration for your motor
    #GPIO.output(MOTOR_PIN_CLOSE, GPIO.LOW)

def main(page: ft.Page):
    page.title = "Motor Control App"

    def show_auto_mode(e):
        page.views.clear()
        page.views.append(auto_mode_view())
        page.update()

    def show_manual_mode(e):
        page.views.clear()
        page.views.append(manual_mode_view())
        page.update()

    def save_time_settings(e):
        try:
            open_hours = int(open_hour_field.value)
            open_minutes = int(open_minute_field.value)
            close_hours = int(close_hour_field.value)
            close_minutes = int(close_minute_field.value)
            
            global open_time, close_time
            open_time = open_hours * 3600 + open_minutes * 60
            close_time = close_hours * 3600 + close_minutes * 60

            saved_time_text.value = f"Saved Open Time: {open_hours}h {open_minutes}m, Close Time: {close_hours}h {close_minutes}m"
            page.update()

        except ValueError:
            status_text.value = "Invalid input! Please enter numeric values for hours and minutes."
            page.update()

    def set_auto_mode(e):
        status_text.value = f"Auto Mode Set: Open for {open_time//3600}h {open_time%3600//60}m, Close for {close_time//3600}h {close_time%3600//60}m"
        page.update()
        page.go("/auto")

        # Automatic mode logic
        while True:
            open_motor()
            motor_status_text.value = "Motor Status: Opened"
            page.update()
            time.sleep(open_time)
            close_motor()
            motor_status_text.value = "Motor Status: Closed"
            page.update()
            time.sleep(close_time)

    def toggle_motor(e):
        nonlocal motor_open
        if motor_open:
            close_motor()
            motor_status_text.value = "Motor Status: Closed Manually"
        else:
            open_motor()
            motor_status_text.value = "Motor Status: Opened Manually"
        motor_open = not motor_open
        page.update()

    def auto_mode_view():
        return ft.View(
            controls=[
                ft.Text("Auto Mode", size=20, weight="bold"),
                ft.Text(value="Adjust the time settings:"),
                open_description, 
                ft.Row([open_hour_field, open_minute_field]), 
                close_description, 
                ft.Row([close_hour_field, close_minute_field]),
                save_button,
                saved_time_text,
                auto_button,
                motor_status_text,
                status_text,
            ]
        )

    def manual_mode_view():
        return ft.View(
            controls=[
                ft.Text("Manual Mode", size=20, weight="bold"),
                manual_button,
                motor_status_text,
            ]
        )

    def home_view():
        return ft.View(
            controls=[
                ft.Text("Motor Control App", size=20, weight="bold"),
                ft.NavigationRail(
                    selected_index=0,
                    min_width=100,
                    min_extended_width=400,
                    
                    destinations=[
                        ft.NavigationRailDestination(
                            icon=ft.icons.AUTORENEW, 
                            label="Auto Mode", 
                            #on_click=show_auto_mode
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.icons.TOGGLE_ON, 
                            label="Manual Mode", 
                            #on_click=show_manual_mode
                        ),
                    ],
                    on_change=lambda e: print("Selected destination:", e.control.selected_index),
                ),
            ],
             
        )

    # Create UI elements
    open_description = ft.Text(value="Set the time to open the motor:")
    open_hour_field = ft.TextField(label="Open Time (hours)", width=100)
    open_minute_field = ft.TextField(label="Open Time (minutes)", width=100)
    
    close_description = ft.Text(value="Set the time to close the motor:")
    close_hour_field = ft.TextField(label="Close Time (hours)", width=100)
    close_minute_field = ft.TextField(label="Close Time (minutes)", width=100)
    
    save_button = ft.ElevatedButton(text="Save Time Settings", on_click=save_time_settings)
    auto_button = ft.ElevatedButton(text="Set Auto Mode", on_click=set_auto_mode)
    manual_button = ft.ElevatedButton(text="Toggle Motor", on_click=toggle_motor)
    status_text = ft.Text(value="")
    saved_time_text = ft.Text(value="")
    motor_status_text = ft.Text(value="Motor Status: Unknown")

    motor_open = False
    open_time = 0
    close_time = 0

    # Initialize with home view
    page.views.append(home_view())

    # Route handling
    def route_change(route):
        if route == "/auto":
            page.views.clear()
            page.views.append(auto_mode_view())
        elif route == "/manual":
            page.views.clear()
            page.views.append(manual_mode_view())
        if route == "/":
            page.views.clear()
            page.views.append(home_view())    
            
        else:
            page.views.clear()
            page.views.append(home_view())
        page.update()

    page.on_route_change = route_change
    page.update()

# Start the Flet app
ft.app(target=main)


