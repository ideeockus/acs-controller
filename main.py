from time import sleep
from typing import List

from device_communication import AccessControlDevice
from database import UsersAccessControl


class DevicePoller:
    devices: List[AccessControlDevice] = []  # список подключенных устройств
    interval = 0.05  # интервал между опросами в секундах

    @classmethod
    def add_device(cls, device: AccessControlDevice):
        cls.devices += device

    @classmethod
    def run_access_control(cls):
        """Запустить бесконечный опрос устройств. Блокирует текущий поток"""
        while True:
            for device in cls.devices:  # для каждого подключенного устройства
                card_uid = device.get_card()  # попробовать считать карту
                if card_uid is not None:
                    # обнаружена карта
                    user = UsersAccessControl.get_user_by_uid(card_uid)
                    if user is None:
                        print(f"Карта с UID {card_uid} не обнаружена!")
                    else:
                        _, fullname = user
                        print(f"Карта с UID {card_uid} принадлежит {fullname}. Открываем..")
                        device.send_open()

            # после каждого цикла опроса небольшой интервал
            sleep(cls.interval)


def main():
    # тут список устройств для опроса
    DevicePoller.add_device(AccessControlDevice(1))  # устройство с slave_id 1

    # запустить опрос
    DevicePoller.run_access_control()


if __name__ == "__main__":
    main()
