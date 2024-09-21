import serial.tools.list_ports
import serial
import tkinter as tk
from tkinter import ttk
import threading
import datetime

def list_available_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def convert_to_four_digit(number):
    return str(number).zfill(4)

# Create a global variable to store the serial connection
ser = None
data_reception_active = False  # Track whether data reception is active

def on_connect_button_click():
    global ser
    selected_port = port_combobox.get()
    if selected_port:
        try:
            ser = serial.Serial(selected_port, baudrate=115200, timeout=1)  # Adjust baudrate and timeout as needed
            result_label.config(text=f"Connected to {selected_port}")
            enable_insulin_pump_controls()
        except serial.SerialException as e:
            result_label.config(text=f"Error: {e}")
    else:
        result_label.config(text="Please select a COM port.")

def enable_insulin_pump_controls():
    lbl.config(state=tk.NORMAL)
    txt.config(state=tk.NORMAL)
    btn_start.config(state=tk.NORMAL)
    btn_prime.config(state=tk.NORMAL)
    btn_reverse.config(state=tk.NORMAL)
    btn_counts.config(state=tk.NORMAL)
    btn_stop.config(state=tk.NORMAL)
    btn_receive.config(state=tk.NORMAL)  # Enable the "Receive" button

def display_value():
    global ser
    try:
        entered_value = txt.get()
        a = float(entered_value) / 100
        result_label_a.config(text=f'{a} ml/hr')
        
        # Send the entered value to the COM port
        if ser:
            ser.write(f'{convert_to_four_digit(entered_value)}'.encode('utf-8'))
    except ValueError:
        result_label_a.config(text="Invalid input")

def prime_action():
    global ser
    try:
        # Implement the functionality for the "Prime" button here
        
        # Send a "Prime" command to the COM port
        if ser:
            ser.write("PR-1".encode('utf-8'))
            
        result_label.config(text="Prime Done")
    except Exception as e:
        result_label.config(text=f"Error: {e}")

def reverse_action():
    global ser
    try:
        # Implement the functionality for the "Reverse" button here
        
        # Send a "Reverse" command to the COM port
        if ser:
            ser.write("RS-0".encode('utf-8'))
            
        result_label.config(text="Rewind Done")
    except Exception as e:
        result_label.config(text=f"Error: {e}")

def stop_action():
    global ser
    try:
        # Send an "ST-2" command to the COM port
        if ser:
            ser.write("ST-2".encode('utf-8'))
            
        result_label.config(text="Stop Done")
    except Exception as e:
        result_label.config(text=f"Error: {e}")
        
def counts_action():
    try:
        entered_value = float(txt.get())
        counts = entered_value * 61809.6506
        counts_label.config(text=f'{counts:.4f} counts/hr')
    except ValueError:
        counts_label.config(text="Invalid input")
        
# Function to start or stop data reception
def toggle_data_reception():
    global data_reception_active
    if data_reception_active:
        # If data reception is active, stop it
        data_reception_active = False
        btn_receive.config(text="Receive")
    else:
        # If data reception is not active, start it
        data_reception_active = True
        btn_receive.config(text="Stop")
        start_data_reception()
        
        
# Function to start data reception in a separate thread
def start_data_reception():
    data_thread = threading.Thread(target=read_and_display_usb_data)
    data_thread.daemon = True
    data_thread.start()    
  
#Function to receive data    
def save_received_data(data):
    try:
        with open('flowrate.txt', 'a') as file:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"[{timestamp}] Received data: {data}\n")
    except Exception as e:
        print(f"Error saving data to file: {e}")
               

# Function to read and display data from the USB device
def read_and_display_usb_data():
    global ser, data_reception_active
    while data_reception_active:
        try:
            if ser and ser.is_open:
                data = ser.readline().decode('utf-8').strip()  # Assuming UTF-8 encoding
                
                # Get the current timestamp
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Display the data with timestamp in the Text widget
                display_data = f"[{timestamp}] Received data: {data}\n"
                data_text.insert(tk.END, display_data)
                data_text.see(tk.END)  # Scroll to the latest data
                
                # Save the data to a text file
                save_received_data(data)

            else:
                break
        except Exception as e:
            print(f"Error in read_and_display_usb_data: {e}")
            
def clear_data():
    data_text.delete(1.0, tk.END)            

# Create the main application window
root = tk.Tk()
root.title("INSULIN PUMP")

# Configure the background color of the root window
root.configure(bg="lightblue")

# Label
label = ttk.Label(root, text="Select a COM port:")
label.pack(pady=10)

# Combobox to select a COM port
available_ports = list_available_ports()
port_combobox = ttk.Combobox(root, values=available_ports)
port_combobox.pack()

# Connect button
connect_button = ttk.Button(root, text="Connect", command=on_connect_button_click)
connect_button.pack(pady=10)

# Label to display the connection status
result_label = ttk.Label(root, text="")
result_label.pack()

# Create a separate frame for insulin pump controls (initially disabled)
insulin_pump_frame = ttk.Frame(root)
insulin_pump_frame.pack(pady=20)

# Label for the text box
lbl = ttk.Label(insulin_pump_frame, text="BASAL RATE:")
lbl.grid(column=0, row=0, padx=10, pady=10)

# Entry Field
txt = ttk.Entry(insulin_pump_frame, width=10)
txt.grid(column=1, row=0, padx=10, pady=10)

# Button to display the entered value
btn_start = ttk.Button(insulin_pump_frame, text="Start", command=display_value)
btn_start.grid(column=2, row=0, padx=10, pady=10)

# Label to display the calculated 'a' value
result_label_a = ttk.Label(insulin_pump_frame, text="")
result_label_a.grid(column=0, row=1, columnspan=3, padx=10, pady=10)

# Label to display counts
counts_label = ttk.Label(insulin_pump_frame, text="")
counts_label.grid(column=0, row=2, columnspan=3, padx=10, pady=10)

# Buttons for insulin pump actions
btn_prime = ttk.Button(insulin_pump_frame, text="Prime", command=prime_action)
btn_prime.grid(column=0, row=3, padx=10, pady=10)

btn_reverse = ttk.Button(insulin_pump_frame, text="Reverse", command=reverse_action)
btn_reverse.grid(column=1, row=3, padx=10, pady=10)

btn_counts = ttk.Button(insulin_pump_frame, text="Counts", command=counts_action)
btn_counts.grid(column=2, row=3, padx=10, pady=10)

btn_stop = ttk.Button(insulin_pump_frame, text="Stop", command=stop_action)
btn_stop.grid(column=0, row=4, padx=10, pady=10)

btn_receive = ttk.Button(insulin_pump_frame, text="Receive", command=toggle_data_reception)
btn_receive.grid(column=1, row=4, padx=10, pady=10)

btn_clear = ttk.Button(insulin_pump_frame, text="Clear", command=clear_data)
btn_clear.grid(column=2, row=4, padx=10, pady=10)

# Disable insulin pump controls initially
lbl.config(state=tk.DISABLED)
txt.config(state=tk.DISABLED)
btn_start.config(state=tk.DISABLED)
btn_prime.config(state=tk.DISABLED)
btn_reverse.config(state=tk.DISABLED)
btn_counts.config(state=tk.DISABLED)
btn_stop.config(state=tk.DISABLED)
btn_receive.config(state=tk.DISABLED)  # Disable the "Receive" button

# Create a Text widget to display received data
data_text = tk.Text(root, height=15, width=60)
data_text.pack(pady=10)

# Function to handle maximizing the window
def maximize_window():
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

# Run the GUI application
root.mainloop()

