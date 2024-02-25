import serial
import time

# Configure serial port
ser = serial.Serial(
    port='/dev/ttyS3',  # Serial port connected to SIM800L
    baudrate=9600,      # Default baud rate for SIM800L
    timeout=1           # Timeout for serial communication
)

# Initialize SIM800L
ser.write(b'AT\r\n')  # Send AT command to check if SIM800L is responding
response = ser.read(100).decode('utf-8')  # Read response
print(response)  # Print response

# Enable text mode for SMS
ser.write(b'AT+CMGF=1\r\n')  # Set SMS mode to text
response = ser.read(100).decode('utf-8')  # Read response
print(response)  # Print response

# Infinite loop to continuously check for incoming messages
while True:
    ser.write(b'AT+CMGL="REC UNREAD"\r\n')  # Command to list unread messages
    response = ser.read(1000).decode('utf-8')  # Read response
    print(response)  # Print response

    # Check if there are any unread messages
    if "+CMT:" in response:
        # Extracting message content
        messages = response.split("+CMT:")
        for msg in messages[1:]:
            parts = msg.split(",")
            sender = parts[0].replace(" ", "")
            date = parts[2].replace('"', "")
            array = parts[3].split('"')
            timeOfText = array[0]
            contentStatus = array[1].split("\r\n\r\n")
            content = contentStatus[0].replace('\r\n', '')

            print("Time: ", timeOfText)
            print("Sender:", sender)
            print("Date:", date)
            print("Content:", content)

    time.sleep(4)  # Wait for 4 seconds before checking again