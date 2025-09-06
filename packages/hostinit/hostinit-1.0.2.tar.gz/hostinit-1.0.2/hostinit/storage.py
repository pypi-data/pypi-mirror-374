##
##

import json
import logging
from hostinit.command import RunShellCommand, RCNotZero
from hostinit.ebsnvme import EbsNvmeDevice

logger = logging.getLogger('hostinit.storage')
logger.addHandler(logging.NullHandler())


class StorageMgrError(Exception):
    pass


class StorageManager(object):

    def __init__(self):
        self.device_list = []
        cmd = ["lsblk", "--json"]

        try:
            output = RunShellCommand().cmd_output(cmd, "/var/tmp")
        except RCNotZero as err:
            raise StorageMgrError(f"can not get disk info: {err}")

        disk_data = json.loads('\n'.join(output))

        for device in disk_data.get('blockdevices', []):
            if device.get('type') == "loop":
                continue
            device_name = f"/dev/{device['name']}"
            part_list = []
            if device.get('children'):
                part_list = [p.get('name') for p in device.get('children')]
            self.device_list.append(dict(name=device_name, partitions=part_list))

    def get_device(self, index: int = 0):
        logger.debug(f"get_device: index: {index} devices: {len(self.device_list)}")
        if index == 0 and len(self.device_list) == 2:
            index = 2
        elif index == 0 and len(self.device_list) >= 3:
            index = 3
        for device in [d.get('name') for d in self.device_list]:
            try:
                logger.debug(f"checking device: {device}")
                dev = EbsNvmeDevice(device)
                name = dev.get_block_device(stripped=True)
                basename = name.split(':')[-1]
                if basename == 'none':
                    continue
                check_name = f"/dev/{basename}"
            except OSError:
                check_name = device
            except TypeError:
                continue

            logger.debug(f"found device: {check_name}")
            if check_name[-1] == chr(ord('`') + index):
                return device

        return None

    def get_partition(self, dev: str, number: int = 1):
        for device in self.device_list:
            if device.get('name') == dev:
                if len(device.get('partitions')) >= number:
                    part_dev = device.get('partitions')[number - 1]
                    return f"/dev/{part_dev}"
        return None

    @property
    def device_count(self) -> int:
        return len(self.device_list)
