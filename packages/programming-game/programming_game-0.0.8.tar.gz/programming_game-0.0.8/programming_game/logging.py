import logging

import rich.box
import rich.traceback
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


def get_logger(name="programming_game"):
    # Prevent duplicate handlers
    # if logger.hasHandlers():
    #    logger.handlers.clear()

    # if not logger.handlers:
    #    monkey_patch_rich_tracebacks()
    #    handler = RichHandler(
    #        rich_tracebacks=True,
    #        tracebacks_code_width=110,
    #        tracebacks_max_frames=10,
    #        tracebacks_extra_lines=1,
    #    )
    #    #handler = logging.StreamHandler()
    #    # Handler zum Logger hinzufügen
    #    logger.addHandler(handler)
    new_logger = logging.getLogger(name)
    new_logger.addHandler(logging.NullHandler())
    new_logger.setLevel(logging.INFO)
    return new_logger


def setup_logging(debug: bool, no_rich_logging: bool = False):
    log = get_logger()

    if log.hasHandlers():
        log.handlers.clear()

    if not no_rich_logging:
        from rich.logging import RichHandler

        monkey_patch_rich_tracebacks()
        handler = RichHandler(
            rich_tracebacks=False,
            # tracebacks_code_width=110,
            # tracebacks_max_frames=10,
            # tracebacks_extra_lines=1,
        )
        log.addHandler(handler)
    else:
        log.addHandler(logging.StreamHandler())

    if debug:
        log.setLevel(logging.DEBUG)


logger = get_logger()
