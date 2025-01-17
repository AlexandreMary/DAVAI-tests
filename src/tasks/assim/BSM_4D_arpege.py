# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, unicode_literals, division

import vortex
from vortex import toolbox
from vortex.layout.nodes import Driver, Family, LoopFamily

from .raw2odb.batodb import BatorODB
from .screenings.screening import Screening
from .minims.minimCNT0 import Minim as MinimCNT0
from .minims.minimOOPS import Minim as MinimOOPS


def setup(t, **kw):
    return Driver(tag='drv', ticket=t, options=kw, nodes=[
        Family(tag='arpege', ticket=t, nodes=[
            Family(tag='4dvar6h', ticket=t, nodes=[
                BatorODB(tag='batodb', ticket=t, **kw),
                Screening(tag='screening', ticket=t, **kw),
                # delayed_fail to let the minimOOPS run before raising error
                MinimCNT0(tag='minimCNT0', ticket=t, on_error='delayed_fail', **kw),
                MinimOOPS(tag='minimOOPS', ticket=t, **kw),
                ], **kw),
            ], **kw),
        ],
    )

