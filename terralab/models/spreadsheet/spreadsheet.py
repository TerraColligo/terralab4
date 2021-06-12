# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import ValidationError # type: ignore
import logging
import re
from .calculate import SpreadsheetCalculate
from .import_all import SpreadsheetImportAll
from .import_demo_orders import SpreadsheetGenerateDemoOrders

logger = logging.getLogger(__name__)

class Spreadsheet(models.Model, SpreadsheetImportAll, SpreadsheetCalculate, SpreadsheetGenerateDemoOrders):
    _name = 'terralab.spreadsheet'
    _inherit = ['mail.thread']
    _description = 'TerraLab Spreadsheet'

    name = fields.Char(track_visibility='onchange', translate=True)
    spreadsheet_url = fields.Char(track_visibility='onchange')
    spreadsheet_id = fields.Char(track_visibility='onchange')
    test_types = fields.One2many('terralab.testtype', 'spreadsheet', 'Test Types', track_visibility='onchange') # Test Types attached to this spreadsheet
    test_products = fields.One2many('product.template', 'terralab_spreadsheet', 'Test Products', track_visibility='onchange') # Test products attached to this spreadsheet
    import_date = fields.Datetime(string='Import Date', readonly=True)
    import_status = fields.Char(readonly=True)

    @api.model
    def create(self, values):
        self._detect_spreadsheet_id(values)
        spreadsheet = super(Spreadsheet, self).create(values)
        return spreadsheet

    def write(self, values):
        self._detect_spreadsheet_id(values)
        super(Spreadsheet, self).write(values)
        logger.info('Writing Spreadsheet %s' % (values))
        return True

    def _detect_spreadsheet_id(self, values):
        new_url = values.get('spreadsheet_url', None)
        if new_url:
            # Extract spreadsheet ID
            m = re.match(r'.*/([^/]+)/edit.*', new_url)
            if m:
                values['spreadsheet_id'] = m.group(1)
            else:
                raise ValidationError('Invalid Spreadsheet URL - Could not detect Spreadsheet ID')
