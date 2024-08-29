import serial
import serial.tools.list_ports
import time


def list_ports():
    """List all available ports and their descriptions."""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
    for port in ports:
        print(
            f"Port: {port.device}, Description: {port.description}, HWID: {port.hwid}"
        )
    return ports


def receive_data(port_name, baudrate=9600):
    """Receive data from the specified serial port."""
    try:
        with serial.Serial(port_name, baudrate, timeout=1) as ser:
            print(f"Listening on {port_name}...")
            while True:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting).decode("utf-8")
                    print(f"Received data: {data}")
                else:
                    # Debug output for empty buffer
                    print(f"No data available at {port_name}.")
                time.sleep(0.1)  # Small delay to avoid high CPU usage
    except serial.SerialException as e:
        print(f"Serial Exception: {e}")
    except OSError as e:
        print(f"OS Error: {e}")


def main():
    ports = list_ports()
    if not ports:
        print("No active serial ports found.")
        return

    # Example: Choose the correct port based on your setup
    port_name = "/dev/ttyS0"  # Update this to the correct port if needed

    receive_data(port_name)


if __name__ == "__main__":
    main()
