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

# This parent class implements Spreadsheet importing for Product Categories
class SpreadsheetImportProductCategories(object):
    def import_product_categories(self: OdooModel, rows: SpreadsheetRows):
        ProductCategory = self.env['product.category']
        logger.info('Importing %s product category row(s)' % (len(rows)))
        col_mapping: SpreadsheetColMapping = {}
        for index, col in enumerate(rows[0]):
            col_mapping[str(col)] = index
        logger.info('Product category column mapping: %s' % (col_mapping))
        for row in rows[1:]:
            logger.debug('PRODUCT CATEGORY: %s' % (row))
            default_code = row[col_mapping['product.category_id']]
            # Check if category already exists
            existing_categories = ProductCategory.search([('terralab_spreadsheet', '=', self.id), ('terralab_default_code', '=', default_code)])
            if len(existing_categories) <= 0:
                # Create new category
                category = ProductCategory.with_context(lang=DEFAULT_LANG).create({
                    'terralab_default_code': default_code,
                    'terralab_spreadsheet': self.id,
                    'name': row[col_mapping['product.category_name en_US']],
                })
                logger.info('CREATE CATEGORY %s %s' % (category, row[col_mapping['product.category_name en_US']]))
            else:
                # Update existing category
                category = existing_categories[0]
                logger.info('UPDATE CATEGORY %s %s' % (category, row[col_mapping['product.category_name en_US']]))
                category.with_context(lang=DEFAULT_LANG).write({
                    'name': row[col_mapping['product.category_name en_US']],
                })
            # Translations (NOT SUPPORTED BY ODOO PRODUCT CATEGORY MODEL!)
            #logger.debug('CATEGORY TRANSLATIONS: %s' % (category))
            #for key, col_num in col_mapping.items():
            #    if key.startswith('product.category_name '):
            #        lang = key[22:]
            #        logger.debug('CATEGORY TRANSLATION %s: %s' % (lang, row[col_num]))
            #        category.with_context(lang=lang).write({
            #            'name': row[col_num],
            #        })
