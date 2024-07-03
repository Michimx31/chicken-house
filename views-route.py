import flet as ft
import time
import json
import os
from datetime import datetime, timedelta
import threading

name = "Chicken Gate Control"

# GPIO setup (commented out for testing without hardware)
# import RPi.GPIO as GPIO
# MOTOR_PIN_OPEN = 17
# MOTOR_PIN_CLOSE = 2
# switch_open_pin = 27  # Magnetic switch for open position
# switch_close_pin = 22  # Magnetic switch for close position

# Gate states
gate_status = ""

# State machine
gate_open = False

# Default open and close times (e.g., 6:00 AM for opening, 6:00 PM for closing)
default_settings = {
    "open_hour": 6,
    "open_minute": 0,
    "close_hour": 18,
    "close_minute": 0
}

# File path for storing settings
SETTINGS_FILE = "gate_settings.json"

# Function to load settings from file
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    else:
        return default_settings

# Function to save settings to file
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

# Load settings at startup
settings = load_settings()
open_hour = settings.get("open_hour", default_settings["open_hour"])
open_minute = settings.get("open_minute", default_settings["open_minute"])
close_hour = settings.get("close_hour", default_settings["close_hour"])
close_minute = settings.get("close_minute", default_settings["close_minute"])

# Motor control functions (simplified for testing without hardware)
def get_gateState():
    global gate_open
    if not gate_open:
        time.sleep(1)
        gate_status = "Open"
        gate_open = True
        return gate_status
    else:
        time.sleep(1)
        gate_status = "Closed"
        gate_open = False
        return gate_status

def open_motor():
    get_gateState()
    while not gate_open:
        time.sleep(0.5)

def close_motor():
    while gate_open:
        get_gateState()
        time.sleep(0.5)

# Function to calculate the remaining time to the next event
def calculate_time_to_next_event():
    now = datetime.now()
    open_time = now.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
    close_time = now.replace(hour=close_hour, minute=close_minute, second=0, microsecond=0)

    if now < open_time:
        return open_time - now, "open"
    elif now < close_time:
        return close_time - now, "close"
    else:
        return (open_time + timedelta(days=1)) - now, "open"

# Function to delay the next event by a specified duration
def delay_next_event(duration):
    global open_hour, open_minute, close_hour, close_minute

    now = datetime.now()
    open_time = now.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0)
    close_time = now.replace(hour=close_hour, minute=close_minute, second=0, microsecond=0)

    if now < open_time:
        open_time += duration
        open_hour, open_minute = open_time.hour, open_time.minute
    elif now < close_time:
        close_time += duration
        close_hour, close_minute = close_time.hour, close_time.minute

    # Save updated settings
    settings.update({
        "open_hour": open_hour,
        "open_minute": open_minute,
        "close_hour": close_hour,
        "close_minute": close_minute
    })
    save_settings(settings)

def main(page: ft.Page):
    global gate_open, open_hour, open_minute, close_hour, close_minute

    def toggle_motor(e):
        
        if gate_open:
            toggle_gate = True
            close_motor()
            if not gate_open:
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
        try:
            open_hours = int(open_hour_dropdown.value)
            open_minutes = int(open_minute_dropdown.value)
            close_hours = int(close_hour_dropdown.value)
            close_minutes = int(close_minute_dropdown.value)

            global open_hour, open_minute, close_hour, close_minute
            open_hour = open_hours
            open_minute = open_minutes
            close_hour = close_hours
            close_minute = close_minutes

            settings = {
                "open_hour": open_hour,
                "open_minute": open_minute,
                "close_hour": close_hour,
                "close_minute": close_minute
            }
            save_settings(settings)

            saved_time_text.value = f"Saved Open Time: {open_hours}h {open_minutes}m, Close Time: {close_hours}h {close_minutes}m"
            page.update()

        except ValueError:
            status_text.value = "Invalid input! Please enter numeric values for hours and minutes."
            page.update()

    # Create dropdown options
    hour_options = [ft.dropdown.Option(str(i)) for i in range(24)]
    minute_options = [ft.dropdown.Option(str(i)) for i in range(60)]

    # Create UI elements
    button = ft.ElevatedButton(text="Toggle Motor", icon=ft.icons.ARROW_CIRCLE_DOWN, on_click=toggle_motor)
    gate_status_text = ft.Text(value="Unknown")

    # Settings UI Elements
    open_description = ft.Text(value="Set the time to open the motor:")
    open_hour_dropdown = ft.Dropdown(label="Open Time (hours)", options=hour_options, value=str(open_hour), width=100)
    open_minute_dropdown = ft.Dropdown(label="Open Time (minutes)", options=minute_options, value=str(open_minute), width=100)
    close_description = ft.Text(value="Set the time to close the motor:")
    close_hour_dropdown = ft.Dropdown(label="Close Time (hours)", options=hour_options, value=str(close_hour), width=100)
    close_minute_dropdown = ft.Dropdown(label="Close Time (minutes)", options=minute_options, value=str(close_minute), width=100)
    save_button = ft.ElevatedButton(text="Save Time Settings", on_click=save_time_settings)
    saved_time_text = ft.Text(value="")
    settings_headline = ft.Text(value="Adjust the time settings:")
    open_settings_row = ft.Row([open_hour_dropdown, open_minute_dropdown])
    close_settings_row = ft.Row([close_hour_dropdown, close_minute_dropdown])
    status_text = ft.Text(value="")

    # Define the images
    close_image = "/house_closed.png"
    open_image = "/house_open.png"

    house_img = ft.Image(
        src=close_image,
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN,
    )

    # Function to update the current time every second
    def update_current_time():
        while True:
            current_time_text.value = f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            page.update()
            time.sleep(1)

    # Function to update the remaining time to the next event
    def update_time_to_next_event():
        while True:
            remaining_time, event = calculate_time_to_next_event()
            remaining_time_text.value = f"Time to next event ({event}): {str(remaining_time).split('.')[0]}"
            page.update()
            time.sleep(1)

    # Create a Text element to display the current time
    current_time_text = ft.Text(value="Current Time: ")
    remaining_time_text = ft.Text(value="")

    # Function to handle delay buttons
    def delay_30min(e):
        delay_next_event(timedelta(minutes=30))
    def delay_60min(e):
        delay_next_event(timedelta(minutes=60))
    def delay_2h(e):
        delay_next_event(timedelta(hours=2))

    delay_30min_button = ft.ElevatedButton(text="Delay 30 min", on_click=delay_30min)
    delay_60min_button = ft.ElevatedButton(text="Delay 60 min", on_click=delay_60min)
    delay_2h_button = ft.ElevatedButton(text="Delay 2 hours", on_click=delay_2h)

    # Define the content areas for different navigation items
    first_content = ft.Column(
        [
            house_img,
            current_time_text,
            remaining_time_text,
            delay_30min_button,
            delay_60min_button,
            delay_2h_button,
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
        expand=True,
    )

    second_content = ft.Column(
        [
            ft.Text("Manual Mode"),
            house_img,
            button,
            gate_status_text
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
        expand=True,
    )

    settings_content = ft.Column(
        [
            settings_headline,
            open_description,
            open_settings_row,
            close_description,
            close_settings_row,
            save_button,
            saved_time_text,
            status_text
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

    # Start background threads to update the current time and remaining time to the next event
    threading.Thread(target=update_current_time, daemon=True).start()
    threading.Thread(target=update_time_to_next_event, daemon=True).start()

# Start the Flet app
ft.app(target=main)
