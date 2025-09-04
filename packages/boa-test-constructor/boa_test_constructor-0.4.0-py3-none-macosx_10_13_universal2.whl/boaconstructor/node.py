import pathlib
import threading
import subprocess
import shlex
import logging
import sys
import time
import yaml
import platform
from neo3.wallet import wallet, account
from neo3.api.wrappers import ChainFacade
from typing import Optional

log = logging.getLogger("neogo")
log.addHandler(logging.StreamHandler(sys.stdout))


class NeoGoNode:
    wallet: wallet.Wallet
    account_committee: account.Account
    facade: ChainFacade

    def __init__(self, config_path: Optional[str] = None):
        self.data_dir = pathlib.Path(__file__).parent.joinpath("data")
        if config_path is None:
            self.config_path = str(self.data_dir.joinpath("protocol.unittest.yml"))
            self.consensus_wallet_path = self.data_dir.joinpath("wallet1_solo.json")
        else:
            self.config_path = config_path
            self.consensus_wallet_path = pathlib.Path(config_path).parent.joinpath(
                "wallet1_solo.json"
            )
        self.system = platform.system().lower()
        self._thread: Optional[threading.Thread] = None
        self._process: Optional[subprocess.Popen[str]] = None
        self._ready = False
        self._terminate = False
        self._parse_config()

    def start(self):
        log.debug("starting")

        prog = "neogo"
        posix = True
        if self.system == "windows":
            prog += ".exe"
            posix = False

        cmd = f"{self.data_dir}/{prog} node --config-file {self.config_path} --relative-path {self.data_dir}"

        self._process = subprocess.Popen(
            shlex.split(cmd, posix=posix),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            shell=False,
        )

        def process_stdout(process):
            for output in iter(process.stdout.readline, b""):
                if "RPC server already started" in output:
                    self._ready = True
                    # WARNING: do not terminate this loop. stdout must be read as long as the process lives otherwise
                    # we'll eventually hit the PIPE buffer limit and hang the child process.
                if self._terminate:
                    break

        self._thread = threading.Thread(target=process_stdout, args=(self._process,))
        self._thread.start()

        while not self._ready:
            time.sleep(0.0001)
        log.debug("running")

    def stop(self):
        log.debug("stopping")
        if self._process is not None:
            self._process.kill()
            self._process.wait()

        if self._thread is not None and self._thread.is_alive():
            self._terminate = True
        log.debug("stopped")

    def reset(self):
        # neo-go uses an in memory database so there's no need to reset anything
        pass

    def _parse_config(self):
        with open(self.config_path) as f:
            config: dict = list(yaml.load_all(f, yaml.FullLoader))[0]
            data = config["ApplicationConfiguration"]

            consensus_wallet_password = data["Consensus"]["UnlockWallet"]["Password"]
            self.wallet = wallet.Wallet.from_file(
                str(self.consensus_wallet_path.absolute()),
                passwords=[
                    consensus_wallet_password,
                    consensus_wallet_password,
                ],
            )
            self.wallet.accounts[0].label = "committee-signature"
            self.wallet.accounts[1].label = "committee"
            self.account_committee = self.wallet.accounts[1]
            self.account_committee = self.wallet.import_multisig_address(
                1, [self.wallet.account_default.public_key]  # type: ignore
            )

            # TODO: warn if port is :0 because then we can't tell where the RPC server is running on
            address = data["RPC"]["Addresses"][0]
            host = f"http://{address}"
            self.facade = ChainFacade(rpc_host=host)
