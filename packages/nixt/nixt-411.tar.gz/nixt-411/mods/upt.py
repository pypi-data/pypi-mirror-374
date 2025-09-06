# This file is placed in the Public Domain.


"uptime"


import time


from nixt.clients import elapsed
from nixt.runtime import STARTTIME


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
