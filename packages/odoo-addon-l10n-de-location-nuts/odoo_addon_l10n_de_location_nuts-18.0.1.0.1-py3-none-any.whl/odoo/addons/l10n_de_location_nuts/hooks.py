# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2015 Tecnativa - Jairo Llopis
# Copyright 2015 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Define German specific configuration in res.country."""
    env = api.Environment(env.cr, SUPERUSER_ID, {})
    germany = env.ref("base.de")
    _logger.info("Setting Germany NUTS configuration")
    germany.write({"state_level": 2})
