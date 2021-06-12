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

logger = logging.getLogger(__name__)

DEFAULT_LANG = 'en_US'

# This parent class implements Spreadsheet importing for Target Use Ranges
class SpreadsheetImportTargetUseRanges(object):
    def import_target_use_ranges(self: OdooModel, rows: SpreadsheetRows):
        TargetUse = self.env['terralab.targetuse']
        TargetUseRange = self.env['terralab.targetuserange']
        TestType = self.env['terralab.testtype']
        logger.info('Importing %s target use range row(s)' % (len(rows)))

        col_mapping = {}
        for index, col in enumerate(rows[0]):
            col_mapping[col] = index
        logger.info('Target use range mapping: %s' % (col_mapping))
        for row in rows[1:]:
            logger.debug('TARGET USE RANGE: %s' % (row))
            target_use_default_code = row[col_mapping['terralab.targetuse']]
            test_default_code = row[col_mapping['terralab.test_name']]
            threshold_1 = row[col_mapping['very_low_threshold']] if col_mapping['very_low_threshold'] < len(row) else ''
            threshold_2 = row[col_mapping['low_threshold']] if col_mapping['low_threshold'] < len(row) else ''
            threshold_3 = row[col_mapping['ideal_value']] if col_mapping['ideal_value'] < len(row) else ''
            threshold_4 = row[col_mapping['high_threshold']] if col_mapping['high_threshold'] < len(row) else ''
            threshold_5 = row[col_mapping['very_high_threshold']] if col_mapping['very_high_threshold'] < len(row) else ''
            num_thresholds = 5 if threshold_1 != '' and threshold_2 != '' and threshold_3 != '' and threshold_4 != '' and threshold_5 != '' else 3
            # Does the referred test exist? Find it
            existing_test_types = TestType.search([('spreadsheet', '=', self.id), ('default_code', '=', test_default_code)])
            if len(existing_test_types) <= 0:
                raise ValidationError('Test Not Found: %s (while adding submitted target use)' % (test_default_code))
            existing_test_type = existing_test_types[0]
            # Does this target use range already exist?
            existing_target_uses = TargetUse.search([('spreadsheet', '=', self.id), ('default_code', '=', target_use_default_code)])
            if len(existing_target_uses) <= 0:
                raise ValidationError('Target Use Not Found: %s (while adding target use range)' % (target_use_default_code))
            existing_target_use = existing_target_uses[0]
            existing_target_use_ranges = TargetUseRange.search([('spreadsheet', '=', self.id), ('target_use', '=', existing_target_use.id), ('test_type', '=', existing_test_type.id)])
            if len(existing_target_use_ranges) <= 0:
                logger.info('ADD TARGET USE RANGE: %s %s' % (existing_target_use, existing_test_type))
                TargetUseRange.with_context(lang=DEFAULT_LANG).create({
                    'spreadsheet': self.id,
                    'target_use': existing_target_use.id,
                    'test_type': existing_test_type.id,
                    'threshold_1': threshold_1,
                    'threshold_2': threshold_2,
                    'threshold_3': threshold_3,
                    'threshold_4': threshold_4,
                    'threshold_5': threshold_5,
                    'num_thresholds': num_thresholds,
                })
            else:
                logger.debug('Target Use Range already exists: %s %s' % (existing_target_use, existing_test_type))
                existing_target_use_ranges[0].with_context(lang=DEFAULT_LANG).write({
                    'threshold_1': threshold_1,
                    'threshold_2': threshold_2,
                    'threshold_3': threshold_3,
                    'threshold_4': threshold_4,
                    'threshold_5': threshold_5,
                    'num_thresholds': num_thresholds,
                })
