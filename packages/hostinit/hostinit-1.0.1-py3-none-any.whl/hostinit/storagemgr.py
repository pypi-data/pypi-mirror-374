##
##

import logging
import time
import warnings
from overrides import override
from hostinit.cli import CLI
from hostinit.storage import StorageManager

warnings.filterwarnings("ignore")
logger = logging.getLogger()


class StorageMgrCLI(CLI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override()
    def local_args(self):
        self.parser.add_argument('-p', '--partition', action='store', help="Get partition for device")
        self.parser.add_argument('-D', '--disk', action='store_true', help="Get disk device")
        self.parser.add_argument('-S', '--swap', action='store_true', help="Get swap device")
        self.parser.add_argument('-R', '--root', action='store_true', help="Get root device")
        self.parser.add_argument('-W', '--wait', action='store_true', help="Wait for device count")
        self.parser.add_argument('-n', '--number', action='store', help="Partition number", type=int, default=0)
        self.parser.add_argument('-t', '--timeout', action='store', type=int, default=60, help="Timeout in seconds to wait for device")

    def run(self):
        if self.options.partition:
            device = StorageManager().get_partition(self.options.partition, self.options.number)
            if device:
                print(device)
        elif self.options.disk:
            device = StorageManager().get_device(self.options.number)
            if device:
                print(device)
        elif self.options.swap:
            device = StorageManager().get_device(2)
            if device:
                print(device)
        elif self.options.root:
            device = StorageManager().get_device(1)
            if device:
                print(device)
        elif self.options.wait:
            count = self.options.number if self.options.number > 0 else 1
            end_time = time.time() + self.options.timeout
            logger.info(f"Waiting {self.options.timeout} seconds for {count} device(s)")
            while StorageManager().device_count < count:
                if time.time() > end_time:
                    logger.error(f"Timeout waiting for device count to reach {count}")
                    break
                time.sleep(1)


def main(args=None):
    cli = StorageMgrCLI(args)
    cli.run()
