# -*- coding: utf-8 -*-
from typing import Any, Dict, List
try:
    from typing import TypedDict # type: ignore
except:
    from typing_extensions import TypedDict
from .types import Spreadsheets, SpreadsheetValueRanges
from ..types import OdooModel, OdooActionResponse
from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import ValidationError # type: ignore
import logging
from googleapiclient.discovery import build # type: ignore
import google.oauth2.credentials # type: ignore
import re
from .import_sample_types import SpreadsheetImportSampleTypes
from .import_tests import SpreadsheetImportTests
from .import_sample_type_allowed_tests import SpreadsheetImportSampleTypeAllowedTests
from .import_product_categories import SpreadsheetImportProductCategories
from .import_products import SpreadsheetImportProducts
from .import_target_uses import SpreadsheetImportTargetUses
from .import_target_use_ranges import SpreadsheetImportTargetUseRanges

logger = logging.getLogger(__name__)

DEFAULT_LANG = 'en_US'

def get_google_spreadsheets(access_token: str) -> Spreadsheets:
    credentials = google.oauth2.credentials.Credentials(access_token)
    service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    sheets = service.spreadsheets()
    return sheets

# This parent class implements Spreadsheet importing.
class SpreadsheetImportAll(SpreadsheetImportSampleTypes, SpreadsheetImportTests, SpreadsheetImportSampleTypeAllowedTests, SpreadsheetImportProductCategories, SpreadsheetImportProducts, SpreadsheetImportTargetUses, SpreadsheetImportTargetUseRanges):
    def action_import_tests_and_products(self: OdooModel) -> OdooActionResponse:
        self.with_context(lang=DEFAULT_LANG).write({
            'import_date': fields.Datetime.now(),
            'import_status': 'in_progress',
        })
        access_token: str = self.env['google.drive.config'].get_access_token(scope='https://spreadsheets.google.com/feeds')
        spreadsheets = get_google_spreadsheets(access_token)
        logger.info('Importing tests from spreadsheet %s' % (self.spreadsheet_id))
        # The ranges that we'll read in one batch operation
        ranges = ['Sample types!A:Z', 'Sample type allowed tests!A:Z', 'Tests!A:Z', 'Products!A:Z', 'Product categories!A:Z', 'Target uses!A:Z', 'Target use ranges!A:Z', 'Odoo!A:Z']
        value_batches = spreadsheets.values().batchGet(spreadsheetId=self.spreadsheet_id, ranges=ranges).execute()
        value_ranges: SpreadsheetValueRanges = value_batches['valueRanges']
        sample_types_range = value_ranges[0]
        sample_type_allowed_tests_range = value_ranges[1]
        tests_range = value_ranges[2]
        products_range = value_ranges[3]
        product_categories_range = value_ranges[4]
        target_uses_range = value_ranges[5]
        target_use_ranges_range = value_ranges[6]
        odoo_range = value_ranges[7]
        self.import_sample_types(sample_types_range['values'])
        self.import_tests(tests_range['values'])
        self.import_product_categories(product_categories_range['values'])
        self.import_target_uses(target_uses_range['values'])
        self.import_target_use_ranges(target_use_ranges_range['values'])
        self.import_sample_type_allowed_tests(sample_type_allowed_tests_range['values'])
        self.import_products(products_range['values'])
        self.with_context(lang=DEFAULT_LANG).write({
            'import_date': fields.Datetime.now(),
            'import_status': 'success',
        })
        self.message_post(body=_('TerraLab imported spreadsheet contents successfully.'))
        return {
            'effect': {
                'fadeout': 'slow',
                'message': _('Spreadsheet imported successfully.'),
                'type': 'rainbow_man',
            }
        }
