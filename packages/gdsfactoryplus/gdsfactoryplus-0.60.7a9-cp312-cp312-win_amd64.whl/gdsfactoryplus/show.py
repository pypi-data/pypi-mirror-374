"""General Show function."""

import io
import sys
from typing import Any

import kfactory as kf
import matplotlib.pyplot as plt

from gdsfactoryplus.core.communication import send_message
from gdsfactoryplus.core.show_cell import show_cell
from gdsfactoryplus.models import ShowBytesMessage


def show(obj: Any = None, /) -> None:
    """Show the object in a human-readable format."""
    match obj:
        case None:
            if plt.get_fignums():
                buf = io.BytesIO()
                plt.gcf().savefig(
                    buf,
                    format="png",
                    bbox_inches="tight",
                )
                msg = ShowBytesMessage.from_buf(buf)
                send_message(msg)
            else:
                sys.stderr.write("No object to show.\n")
        case kf.ProtoTKCell():
            from gdsfactoryplus.logger import get_logger

            get_logger().warning(f"{obj}")
            show_cell(obj)
