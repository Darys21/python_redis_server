import re
from enum import Enum
import asyncio

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
    async def parse_resp_array_request(reader):
        try:
            first_byte = await reader.read(1)
            if first_byte == DataType.ARRAY.value:
                array_length = int((await reader.readline()).strip())
                commands = []
                for _ in range(array_length):
                    command_type = await reader.read(1)
                    if command_type == DataType.BULK_STRING.value:
                        command_length = int((await reader.readline()).strip())
                        command = (await reader.read(command_length)).decode()
                        commands.append(command)
                        await reader.read(2)  # Consume the \r\n
                    else:
                        raise ValueError("Unsupported command type")
                return commands, commands
            else:
                raise ValueError("Expected array type")
        except Exception as e:
            print(f"Error parsing RESP array request: {e}")
            return None, None

    @staticmethod
    async def parse_resp_simple_string(reader):
        try:
            if (await reader.read(1)) == DataType.SIMPLE_STRING.value:
                return (await reader.readline()).strip()
            else:
                raise ValueError("Expected simple string type")
        except Exception as e:
            print(f"Error parsing RESP simple string: {e}")
            return None

    @staticmethod
    async def parse_resp_bulk_string(reader):
        try:
            if (await reader.read(1)) == DataType.BULK_STRING.value:
                length = int((await reader.readline()).strip())
                if length == -1:
                    return None
                data = await reader.read(length)
                await reader.read(2)  # Consume the \r\n
                return data
            else:
                raise ValueError("Expected bulk string type")
        except Exception as e:
            print(f"Error parsing RESP bulk string: {e}")
            return None

    @staticmethod
    async def parse_resp_integer(reader):
        try:
            if (await reader.read(1)) == DataType.INTEGER.value:
                return int((await reader.readline()).strip())
            else:
                raise ValueError("Expected integer type")
        except Exception as e:
            print(f"Error parsing RESP integer: {e}")
            return None

    @staticmethod
    async def parse_resp_error(reader):
        try:
            if (await reader.read(1)) == DataType.ERROR.value:
                return (await reader.readline()).strip()
            else:
                raise ValueError("Expected error type")
        except Exception as e:
            print(f"Error parsing RESP error: {e}")
            return None