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

# This parent class implements Spreadsheet importing for Sample Types.
class SpreadsheetImportSampleTypes(object):
    def import_sample_types(self: OdooModel, rows: SpreadsheetRows):
        SampleType = self.env['terralab.sampletype']
        Translation = self.env['ir.translation']
        logger.info('Importing %s sample type row(s)' % (len(rows)))
        col_mapping: SpreadsheetColMapping = {}
        for index, col in enumerate(rows[0]):
            col_mapping[str(col)] = index
        logger.info('Sample type column mapping: %s' % (col_mapping))
        for row in rows[1:]:
            logger.debug('SAMPLE TYPE: %s' % (row))
            default_code = row[col_mapping['sample_type.id']]
            # Check if sample type already exists
            existing_sample_types = SampleType.search([('spreadsheet', '=', self.id), ('default_code', '=', default_code)])
            if len(existing_sample_types) <= 0:
                # Create new sample type
                sample_type = SampleType.with_context(lang=DEFAULT_LANG).create({
                    'default_code': default_code,
                    'spreadsheet': self.id,
                    'name': row[col_mapping['sample_type.name en_US']],
                })
            else:
                # Update existing category
                sample_type = existing_sample_types[0]
                sample_type.with_context(lang=DEFAULT_LANG).write({
                    'name': row[col_mapping['sample_type.name en_US']],
                })
            # Translations
            logger.debug('SAMPLE TYPE TRANSLATIONS: %s' % (sample_type))
            for key, col_num in col_mapping.items():
                if key.startswith('sample_type.name '):
                    lang = key[17:]
                    sample_type.with_context(lang=lang).write({
                        'name': row[col_num]
                    })
