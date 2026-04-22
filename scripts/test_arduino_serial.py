from smartmed.hardware.serial_transport import ArduinoSerialTransport
from smartmed.services.dispense_service import dispense_slot, ping_arduino


def main() -> None:
    transport = ArduinoSerialTransport()

    try:
        print("Sende PING ...")
        ping_result = ping_arduino(transport)
        print("PING-Ergebnis:", ping_result)

        print("Sende DISPENSE 1 1 ...")
        dispense_result = dispense_slot(transport, slot=1, count=1)
        print("DISPENSE-Ergebnis:", dispense_result)

    finally:
        transport.close()


if __name__ == "__main__":
    main()