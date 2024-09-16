import serial

class Monocromador:
    
    def __init__(self, port: str):
        self.ser = serial.Serial(port, 9600,  parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
        self.set_echo(False)
        pass
    
    def __send_command(self, command: str):
        command_with_end = command + "\r\n"
        self.ser.write(command_with_end.encode("ascii"))
        pass
    
    def __receive_command(self) -> str:
        response = self.ser.readline()
        return response.decode("ascii")
    
    def set_echo(self, set: bool):
        self.__send_command("ECHO " + "1" if set else "0")
        pass
    
    def get_echo(self) -> bool:
        self.__send_command("ECHO?")
        response = self.__receive_command()
        value = int(response)
        return True if value == 1 else False
    
    def store_wavelength(self, wavelength: float):
        self.__send_command(f"GOWAVE {wavelength}")
        pass
    
    def get_wavelength(self) -> float:
        self.__send_command("GOWAVE?")
        response = self.__receive_command()
        return float(response)
    
