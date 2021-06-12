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

# This parent class implements Spreadsheet importing for Products
class SpreadsheetImportProducts(object):
    def import_products(self: OdooModel, rows: SpreadsheetRows):
        Product = self.env['product.template']
        ProductCategory = self.env['product.category']
        TestType = self.env['terralab.testtype']
        logger.info('Importing %s product row(s)' % (len(rows)))
        col_mapping: SpreadsheetColMapping = {}
        for index, col in enumerate(rows[0]):
            col_mapping[str(col)] = index
        logger.info('Product column mapping: %s' % (col_mapping))

        product_map = {}
        for row in rows[1:]:
            default_code = row[col_mapping['product.default_code']]
            if not default_code in product_map:
                # First instance of product
                product_map[default_code] = {
                    'row': row,
                    'tests': [row[col_mapping['terralab.test_name']]]
                }
            else:
                # Continuing same product, just add the test name
                product_map[default_code]['tests'].append(row[col_mapping['terralab.test_name']])

        for default_code, product_def in product_map.items():
            logger.debug('PRODUCT: %s %s' % (default_code, product_def['tests']))
            row = product_def['row']

            # Lookup related tests
            test_type_ids = []
            for test_name in product_def['tests']:
                existing_test_types = TestType.search([('spreadsheet', '=', self.id), ('default_code', '=', test_name)])
                if len(existing_test_types) > 0:
                    test_type_ids.append(existing_test_types[0].id)

            # Lookup related category
            existing_categories = ProductCategory.search([('terralab_spreadsheet', '=', self.id), ('terralab_default_code', '=', row[col_mapping['product.category_id']])])
            if len(existing_categories) > 0:
                category_id = existing_categories[0].id
            else:
                raise ValidationError('Category Not Found: %s' % (row[col_mapping['product.category_id']]))
                category_id = None

            # Check if product already exists
            existing_products = Product.search([('terralab_spreadsheet', '=', self.id), ('default_code', '=', default_code)])
            if len(existing_products) <= 0:
                # Create new product
                product = Product.with_context(lang=DEFAULT_LANG).create({
                    'default_code': default_code,
                    'terralab_spreadsheet': self.id,
                    'terralab_test_types': test_type_ids,
                    'categ_id': category_id,
                    'type': 'service',
                    'name': row[col_mapping['product.name en_US']] if col_mapping['product.name en_US'] < len(row) else None,
                    'barcode': (row[col_mapping['product.barcode']] if col_mapping['product.barcode'] < len(row) else None) or None,
                    'list_price': row[col_mapping['product.list_price']] if col_mapping['product.list_price'] < len(row) else None,
                    'description': row[col_mapping['product.description en_US']] if col_mapping['product.description en_US'] < len(row) else None,
                })
            else:
                # Update existing product
                product = existing_products[0]
                product.with_context(lang=DEFAULT_LANG).write({
                    'terralab_test_types': test_type_ids,
                    'categ_id': category_id,
                    'type': 'service',
                    'name': row[col_mapping['product.name en_US']] if col_mapping['product.name en_US'] < len(row) else None,
                    'barcode': (row[col_mapping['product.barcode']] if col_mapping['product.barcode'] < len(row) else None) or None,
                    'list_price': row[col_mapping['product.list_price']] if col_mapping['product.list_price'] < len(row) else None,
                    'description': row[col_mapping['product.description en_US']] if col_mapping['product.description en_US'] < len(row) else None,
                })
            # Translations
            logger.debug('PRODUCT TRANSLATIONS: %s' % (product))
            for key, col_num in col_mapping.items():
                if key.startswith('product.name '):
                    lang = key[13:]
                    if col_num < len(row):
                        logger.debug('PRODUCT NAME TRANSLATION %s: %s' % (lang, row[col_num]))
                        product.with_context(lang=lang).write({
                            'name': row[col_num],
                        })
                if key.startswith('product.description '):
                    lang = key[20:]
                    if col_num < len(row):
                        logger.debug('PRODUCT DESCRIPTION TRANSLATION %s: %s' % (lang, row[col_num]))
                        product.with_context(lang=lang).write({
                            'description': row[col_num],
                        })
