##
##

import logging
import warnings
import sys
import ansible_runner
from overrides import override
from hostinit.cli import CLI, StreamOutputLogger
from hostinit import get_playbook_file

warnings.filterwarnings("ignore")
logger = logging.getLogger()


class BundleMgrCLI(CLI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override()
    def local_args(self):
        self.parser.add_argument('-b', '--bundles', nargs='+', help='List of bundles to deploy')
        self.parser.add_argument('-V', '--version', action='store', help="Software version", default="latest")
        self.parser.add_argument('-D', '--dns', action='store', help="DNS server", default="8.8.8.8")

    def is_time_synced(self):
        return self.host_info.system.is_running("ntp") \
            or self.host_info.system.is_running("ntpd") \
            or self.host_info.system.is_running("systemd-timesyncd") \
            or self.host_info.system.is_running("chrony") \
            or self.host_info.system.is_running("chronyd")

    def is_firewalld_enabled(self):
        return self.host_info.system.is_running("firewalld")

    def run(self):
        os_name = self.op.os.os_name
        os_major = self.op.os.os_major_release
        os_minor = self.op.os.os_minor_release
        os_arch = self.op.os.architecture
        logger.info(f"Running on {os_name} version {os_major} {os_arch}")
        extra_vars = {
            'package_root': self.data,
            'os_name': os_name,
            'os_major': os_major,
            'os_minor': os_minor,
            'os_arch': os_arch,
            'time_svc_enabled': self.is_time_synced(),
            'firewalld_enabled': self.is_firewalld_enabled()
        }

        for b in self.options.bundles:
            self.op.add(b)

        self.run_timestamp("begins")

        for bundle in self.op.install_list():
            logger.info(f"Executing bundle {bundle.name}")
            for playbook in [bundle.pre, bundle.run, bundle.post]:
                if not playbook:
                    continue
                for extra_var in bundle.extra_vars:
                    logger.info(f"Getting value for variable {extra_var}")
                    if extra_var == "dns_server":
                        dns_server = self.options.dns
                        extra_vars.update({'dns_server': dns_server})
                logger.info(f"Running playbook {playbook}")
                stdout_save = sys.stdout
                sys.stdout = StreamOutputLogger(logger, logging.INFO)
                r = ansible_runner.run(playbook=f"{get_playbook_file(playbook)}", extravars=extra_vars)
                sys.stdout = stdout_save
                logger.info(f"Playbook status: {r.status}")
                if r.rc != 0:
                    logger.error(r.stats)
                    self.run_timestamp("failed")
                    sys.exit(r.rc)

        self.run_timestamp("successful")


def main(args=None):
    cli = BundleMgrCLI(args)
    cli.run()
