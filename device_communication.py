import struct
from typing import Optional
import serial
import threading


def crc16(buf: bytearray, byteorder='little', crcmod=None) -> bytes:
    crc16_fn = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True, xorOut=0x0000)
    crc16_val = crc16_fn(buf)
    return crc16_val.to_bytes(2, byteorder=byteorder)


def check_crc(packet: bytearray) -> bool:
    packet_crc = packet[-2:]  # crc из пакета
    calculated_crc = crc16(packet_crc[:-2])

    return packet_crc == calculated_crc


class UartInterface:
    dev_name = "/dev/ttyAMA0"   # соответствует UART0
    port = serial.Serial(dev_name, 9600)  # параметры порта 9600 8N1
    uart_mutex = threading.Lock()  # для блокировки порта на время запроса

    @classmethod
    def read_and_write_bytes_request(cls, req_buf: bytearray, resp_size: int) -> Optional[bytearray]:
        with cls.uart_mutex:  # на время запроса порт блокируется, т.е. к нему не будет доступа из другого потока
            cls.port.write(req_buf)  # отправить запрос
            resp_buf = cls.port.read(resp_size)  # прочитать resp_size байт ответа
            return bytearray(resp_buf) if resp_buf else None


class AccessControlDevice:
    def __init__(self, slave_id: int):
        self.slave_id = slave_id  # адрес устройства
        self.read_card_addr = bytearray([2])  # адрес регистра, в котором записан uid поднесенной карты или ноль
        self.write_state = bytearray([2])  # адрес регистра для управления (открыть)

    def build_packet(self, payload: bytearray) -> bytearray:
        packet_crc16 = crc16(bytearray([self.slave_id]))
        packet = bytearray([self.slave_id]) + payload + packet_crc16
        return packet

    def get_card(self) -> Optional[int]:
        """Запрос на получение uid поднесенной карты"""
        req_buf_payload = bytearray([3]) + self.read_card_addr + bytearray([2])
        req_buf = self.build_packet(req_buf_payload)
        resp_buf = UartInterface.read_and_write_bytes_request(req_buf, 9)  # отправить запрос и прочитать 9 байт ответа

        if not check_crc(resp_buf):
            raise ValueError("Неправильный CRC ответа")

        card_uid = struct.unpack("<I", resp_buf[3:7])  # распаковать байты в unsigned int

        return card_uid if card_uid != 0 else None

    def send_open(self) -> bool:
        print(f"Запрос на открытие для {self.slave_id}")
        req_buf = self.build_packet(bytearray([5]) + self.write_state + bytearray([0xff, 0x00]))
        resp_buf = UartInterface.read_and_write_bytes_request(req_buf, 8)

        return resp_buf == req_buf  # true если успешно
