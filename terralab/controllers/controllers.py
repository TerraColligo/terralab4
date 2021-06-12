# -*- coding: utf-8 -*-
from odoo import http # type: ignore
from odoo.http import request # type: ignore
import logging
import sys
import traceback

logger = logging.getLogger(__name__)

class TerraLab(http.Controller):
    @http.route('/terralab/mass-edit-tests/', website=True)
    def mass_edit_tests(self, **kw):
        return request.render('terralab.mass_edit_tests')
