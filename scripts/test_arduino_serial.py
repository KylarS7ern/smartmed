from smartmed.hardware.protocol import build_dispense_command, build_ping_command
from smartmed.hardware.serial_transport import (
    ArduinoSerialError,
    ArduinoSerialTransport,
)


def main() -> None:
    transport = ArduinoSerialTransport()

    try:
        print("Sende PING ...")
        ping_response = transport.transact(build_ping_command())
        print("Antwort auf PING:", ping_response)

        print("Sende DISPENSE 1 1 ...")
        dispense_response = transport.transact(build_dispense_command(1, 1))
        print("Antwort auf DISPENSE:", dispense_response)

    except ArduinoSerialError as exc:
        print("ArduinoSerialError:", exc)

    finally:
        transport.close()


if __name__ == "__main__":
    main()
    