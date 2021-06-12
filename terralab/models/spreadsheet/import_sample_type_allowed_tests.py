# -*- coding: utf-8 -*-
from typing import Any, Dict, List
try:
    from typing import TypedDict # type: ignore
except:
    from typing_extensions import TypedDict
from .types import SpreadsheetRows, SpreadsheetColMapping
from ..types import OdooModel, OdooActionResponse
from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import ValidationError # type: ignore
import logging
import re

SampleTestMapping = Dict

logger = logging.getLogger(__name__)

DEFAULT_LANG = 'en_US'

# This parent class implements Spreadsheet importing for Sample Type Allowed Tests.
class SpreadsheetImportSampleTypeAllowedTests(object):
    # Call import_samples() and import_tests() before calling this
    def import_sample_type_allowed_tests(self: OdooModel, rows: SpreadsheetRows):
        SampleType = self.env['terralab.sampletype']
        TestType = self.env['terralab.testtype']
        logger.info('Importing %s sample type allowed test row(s)' % (len(rows)))
        col_mapping: SpreadsheetColMapping = {}
        for index, col in enumerate(rows[0]):
            col_mapping[str(col)] = index
        logger.info('Sample type allowed test column mapping: %s' % (col_mapping))
        sample_test_mapping: SampleTestMapping = {}
        for row in rows[1:]:
            #logger.info('SAMPLE TYPE ALLOWED TEST: %s' % (row))
            sample_type_id = row[col_mapping['sample_type.id']]
            test_name = row[col_mapping['terralab.test_name']]
            if not sample_type_id in sample_test_mapping:
                sample_test_mapping[sample_type_id] = set()
            existing_test_types = TestType.search([('spreadsheet', '=', self.id), ('default_code', '=', test_name)])
            if len(existing_test_types) > 0:
                sample_test_mapping[sample_type_id].add(existing_test_types[0].id)
        for sample_type_id, test_type_ids in sample_test_mapping.items():
            logger.debug('SAMPLE TYPE %s ALLOWED TESTS %s' % (sample_type_id, test_type_ids))
            existing_sample_types = SampleType.search([('spreadsheet', '=', self.id), ('default_code', '=', sample_type_id)])
            if len(existing_sample_types) <= 0:
                raise ValidationError('Sample Type Not Found: %s (while setting allowed tests)' % (sample_type_id))
            existing_sample_types.with_context(lang=DEFAULT_LANG).write({
                'test_types': list(test_type_ids),
            })
