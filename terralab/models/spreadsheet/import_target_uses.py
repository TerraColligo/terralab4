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

# This parent class implements Spreadsheet importing for Target Uses
class SpreadsheetImportTargetUses(object):
    def import_target_uses(self: OdooModel, rows: SpreadsheetRows):
        TargetUse = self.env['terralab.targetuse']
        Translation = self.env['ir.translation']
        logger.info('Importing %s target use row(s)' % (len(rows)))
        col_mapping: SpreadsheetColMapping = {}
        for index, col in enumerate(rows[0]):
            col_mapping[str(col)] = index
        logger.info('Target use column mapping: %s' % (col_mapping))
        for row in rows[1:]:
            logger.debug('TARGET USE: %s' % (row))
            default_code = row[col_mapping['terralab.targetuse']]
            # Does this target use already exist?
            existing_target_uses = TargetUse.search([('spreadsheet', '=', self.id), ('default_code', '=', default_code)])
            if len(existing_target_uses) <= 0:
                # Create new
                target_use = TargetUse.with_context(lang=DEFAULT_LANG).create({
                    'default_code': default_code,
                    'spreadsheet': self.id,
                    'name': row[col_mapping['terralab.targetuse en_US']],
                })
            else:
                # Update existing
                target_use = existing_target_uses[0]
                target_use.with_context(lang=DEFAULT_LANG).write({
                    'name': row[col_mapping['terralab.targetuse en_US']],
                })
            # Translations
            logger.debug('TARGET USE TRANSLATIONS: %s' % (target_use))
            for key, col_num in col_mapping.items():
                if key.startswith('terralab.targetuse '):
                    lang = key[19:]
                    logger.debug('TARGET USE TRANSLATION %s: %s' % (lang, row[col_num]))
                    target_use.with_context(lang=lang).write({
                        'name': row[col_num],
                    })
