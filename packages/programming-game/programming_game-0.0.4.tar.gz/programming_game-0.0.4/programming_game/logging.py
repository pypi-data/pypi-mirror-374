import json
import logging
from datetime import datetime

import rich.box
import rich.traceback
from rich.logging import RichHandler
from rich.panel import Panel


def monkey_patch_rich_tracebacks():
    panel_init_original = Panel.__init__

    def panel_init_fixed(self, *args, **kwargs):
        is_traceback_panel = "Traceback" in kwargs.get("title", "")
        if is_traceback_panel:
            box_pycharm_compatible = rich.box.MINIMAL_DOUBLE_HEAD
            kwargs["box"] = box_pycharm_compatible

            for arg in args:
                # handle rich code that passes Box as a positional arg
                if isinstance(arg, rich.box.Box):
                    args = list(args)
                    args.remove(arg)
                    args = tuple(args)

        panel_init_original(self, *args, **kwargs)

    Panel.__init__ = panel_init_fixed

    rich.traceback.install(width=300)


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_record["extra"] = record.extra
        return json.dumps(log_record)


def get_logger(name="programming_game"):
    TRACE_LEVEL_NUM = 5
    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE_LEVEL_NUM):
            self._log(TRACE_LEVEL_NUM, message, args, **kws)

    logging.Logger.trace = trace

    SUCCESS_LEVEL_NUM = 25
    logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

    def success(self, message, *args, **kws):
        if self.isEnabledFor(SUCCESS_LEVEL_NUM):
            self._log(SUCCESS_LEVEL_NUM, message, args, **kws)

    logging.Logger.success = success

    logger = logging.getLogger(name)
    logger.setLevel("DEBUG")

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    if not logger.handlers:
        monkey_patch_rich_tracebacks()
        handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_code_width=110,
            tracebacks_max_frames=10,
            tracebacks_extra_lines=1,
        )
        #handler = logging.StreamHandler()
        # Handler zum Logger hinzufügen
        logger.addHandler(handler)

    return logger


logger = get_logger()
