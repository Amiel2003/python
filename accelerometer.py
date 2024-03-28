import smbus
import time
import OPi.GPIO as GPIO
from gps import read_gps_data

GPIO.setmode(GPIO.BOARD)

# ADXL345 registers
ADXL345_ADDRESS = 0x53
REG_POWER_CTL = 0x2D
REG_DATA_FORMAT = 0x31
REG_DATAX0 = 0x32
THRESHOLD = 1.8
LED_PIN_1 = 12
LED_PIN_2 = 15
BUZZER_PIN = 26
MESSAGE_PIN= 12
BUTTON_PIN = 23

# Configure I2C
bus = smbus.SMBus(0)  # Use /dev/i2c-1, adjust if necessary

def adxl345_setup():
    # Set data format to full resolution (±16g range)
    bus.write_byte_data(ADXL345_ADDRESS, REG_DATA_FORMAT, 0x0B)
    # Enable measurement mode
    bus.write_byte_data(ADXL345_ADDRESS, REG_POWER_CTL, 0x08)

    # Set up GPIO for LED
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.setup(LED_PIN_1, GPIO.OUT)
    GPIO.setup(LED_PIN_2, GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.output(LED_PIN_1, GPIO.LOW)
    GPIO.output(LED_PIN_2, GPIO.LOW)

def read_acceleration():
    # Read 6 bytes of data from ADXL345 (X0, X1, Y0, Y1, Z0, Z1)
    data = bus.read_i2c_block_data(ADXL345_ADDRESS, REG_DATAX0, 6)
    # Combine the two bytes for each axis and convert to signed values
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]
    # Convert to signed values
    x = x if x < 32768 else x - 65536
    y = y if y < 32768 else y - 65536
    z = z if z < 32768 else z - 65536
    return {'x': round(x/256.0, 2), 'y': round(y/256.0, 2), 'z': round(z/256.0, 2)}

def detect_collision(acceleration):
    try:
        # Blink the LED for visual indication
        for _ in range(50):
            button_state = GPIO.input(BUTTON_PIN)
            if(button_state == GPIO.HIGH):
                return False
                break

            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            GPIO.output(LED_PIN_1, GPIO.HIGH)
            GPIO.output(LED_PIN_2, GPIO.HIGH)
            time.sleep(0.1)

            GPIO.output(BUZZER_PIN, GPIO.LOW)
            GPIO.output(LED_PIN_1, GPIO.LOW)
            GPIO.output(LED_PIN_2, GPIO.LOW)
            time.sleep(0.1)

        # Check if any acceleration value exceeds the threshold
        if any(abs(value) > THRESHOLD or value < -THRESHOLD for value in acceleration.values()):
            return True

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.output(BUZZER_PIN, GPIO.LOW)  # Ensure the LED is off before returning
        GPIO.output(LED_PIN_1, GPIO.LOW)
        GPIO.output(LED_PIN_2, GPIO.LOW)

    return False

if __name__ == "__main__":
    try:
        adxl345_setup()
        while True:
            acceleration = read_acceleration()
            print(f"X: {acceleration['x']}, Y: {acceleration['y']}, Z: {acceleration['z']}")

            if any(abs(value) > THRESHOLD or value < -THRESHOLD for value in acceleration.values()):
                if detect_collision(acceleration):
                    print("Sending emergency!")
                    read_gps_data('/dev/ttyUSB0')
                    for _ in range (3):
                        GPIO.output(BUZZER_PIN, GPIO.HIGH)
                        GPIO.output(LED_PIN_1, GPIO.HIGH)
                        GPIO.output(LED_PIN_2, GPIO.HIGH)
                        time.sleep(0.5)

                        GPIO.output(BUZZER_PIN, GPIO.LOW)
                        GPIO.output(LED_PIN_1, GPIO.LOW)
                        GPIO.output(LED_PIN_2, GPIO.LOW)
                        time.sleep(0.5)

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")
    finally:
        GPIO.cleanup()