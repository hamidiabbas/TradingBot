import MetaTrader5 as mt5
from utils.logger import get_logger
from utils.config import CONFIG

log = get_logger("MT5Connector", CONFIG["logging_level"])

class MT5Connector:
    def __init__(self):
        self.initialized = False

    def initialize(self) -> bool:
        # initialize/login per MQL5 docs[17][18]
        mt5_path = CONFIG["MT5"]["path"]
        timeout = CONFIG["MT5"]["timeout_ms"]
        if mt5_path:
            ok = mt5.initialize(mt5_path, timeout=timeout)
        else:
            ok = mt5.initialize(timeout=timeout)
        if not ok:
            log.error(f"MT5 initialize() failed: {mt5.last_error()}")
            return False
        login = CONFIG["MT5"]["login"]
        if login:
            ok_login = mt5.login(
                login, password=CONFIG["MT5"]["password"], server=CONFIG["MT5"]["server"], timeout=timeout
            )
            if not ok_login:
                log.error(f"MT5 login() failed: {mt5.last_error()}")
                return False
        self.initialized = True
        ver = mt5.version()
        log.info(f"MT5 connected. Version={ver}")
        return True

    def select_symbol(self, symbol: str) -> bool:
        # ensure symbol is in Market Watch[23]
        info = mt5.symbol_info(symbol)
        if info is None:
            log.error(f"symbol_info failed for {symbol}: {mt5.last_error()}")
            return False
        if not info.visible:
            if not mt5.symbol_select(symbol, True):
                log.error(f"symbol_select failed for {symbol}: {mt5.last_error()}")
                return False
        return True

    def shutdown(self):
        if self.initialized:
            mt5.shutdown()  # per official docs[9][18]
            log.info("MT5 shutdown complete")
            self.initialized = False
