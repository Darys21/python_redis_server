import re
from enum import Enum

class DataType(Enum):
    SIMPLE_STRING = b'+'
    ERROR = b'-'
    INTEGER = b':'
    BULK_STRING = b'$'
    ARRAY = b'*'

class Constant:
    TERMINATOR = b'\r\n'
    EMPTY_BYTE = b''
    SPACE_BYTE = b' '
    PONG = b'PONG'
    OK = b'OK'
    INVALID_COMMAND = b'Invalid command'
    NULL_BULK_STRING = b'$-1\r\n'
    FULLRESYNC = b'FULLRESYNC'

class Command(Enum):
    PING = 'ping'
    ECHO = 'echo'
    GET = 'get'
    SET = 'set'
    INFO = 'info'
    REPLCONF = 'replconf'
    PSYNC = 'psync'
    FULLRESYNC = 'fullresync'
    WAIT = 'wait'
    CONFIG = 'config'
    ACK = 'ack'

class RESPParser:
    @staticmethod
    def parse_resp_array_request(reader):
        try:
            first_byte = reader.read(1)
            if first_byte == DataType.ARRAY.value:
                array_length = int(reader.readline().strip())
                commands = []
                for _ in range(array_length):
                    command_type = reader.read(1)
                    if command_type == DataType.BULK_STRING.value:
                        command_length = int(reader.readline().strip())
                        command = reader.read(command_length).decode()
                        commands.append(command)
                        reader.read(2)  # Consume the \r\n
                    else:
                        raise ValueError("Unsupported command type")
                return commands, commands
            else:
                raise ValueError("Expected array type")
        except Exception as e:
            print(f"Error parsing RESP array request: {e}")
            return None, None

    @staticmethod
    def parse_resp_simple_string(reader):
        try:
            if reader.read(1) == DataType.SIMPLE_STRING.value:
                return reader.readline().strip()
            else:
                raise ValueError("Expected simple string type")
        except Exception as e:
            print(f"Error parsing RESP simple string: {e}")
            return None

    @staticmethod
    def parse_resp_bulk_string(reader):
        try:
            if reader.read(1) == DataType.BULK_STRING.value:
                length = int(reader.readline().strip())
                if length == -1:
                    return None
                data = reader.read(length)
                reader.read(2)  # Consume the \r\n
                return data
            else:
                raise ValueError("Expected bulk string type")
        except Exception as e:
            print(f"Error parsing RESP bulk string: {e}")
            return None

    @staticmethod
    def parse_resp_integer(reader):
        try:
            if reader.read(1) == DataType.INTEGER.value:
                return int(reader.readline().strip())
            else:
                raise ValueError("Expected integer type")
        except Exception as e:
            print(f"Error parsing RESP integer: {e}")
            return None

    @staticmethod
    def parse_resp_error(reader):
        try:
            if reader.read(1) == DataType.ERROR.value:
                return reader.readline().strip()
            else:
                raise ValueError("Expected error type")
        except Exception as e:
            print(f"Error parsing RESP error: {e}")
            return None