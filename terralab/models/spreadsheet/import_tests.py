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

CurrentTest = Dict

logger = logging.getLogger(__name__)

DEFAULT_LANG = 'en_US'

# This parent class implements Spreadsheet importing for Tests.
class SpreadsheetImportTests(object):
    def import_tests(self: OdooModel, rows: SpreadsheetRows):
        TestType = self.env['terralab.testtype']
        #Uom = self.env['uom.uom']
        logger.info('Importing %s test row(s)' % (len(rows)))
        col_mapping = {}
        for index, col in enumerate(rows[0]):
            col_mapping[col] = index
        logger.info('Test column mapping: %s' % (col_mapping))
        current_test: CurrentTest = {}

        def save_test_variables(test_type, current_test):
            TestVariableType = self.env['terralab.testvariabletype']
            logger.debug('TEST VARIABLES FOR %s' % (test_type))
            existing_test_variable_types = TestVariableType.search([('spreadsheet', '=', self.id), ('test_type', '=', test_type.id)])
            logger.debug(' Existing variables: %s' % (existing_test_variable_types))
            for key, item in current_test.items():
                if key.startswith('terralab.variable_') and item.get('name'):
                    var_num = int(key[18:])
                    test_variable_type = None
                    for existing_test_variable_type in existing_test_variable_types:
                        if existing_test_variable_type.num == var_num:
                            test_variable_type = existing_test_variable_type
                            break
                    if test_variable_type:
                        logger.debug(' - UPDATE VAR %s %s %s' % (var_num, item['name'], item['name_translations']))
                        test_variable_type.with_context(lang=DEFAULT_LANG).write({
                            'name': item['name'],
                        })
                    else:
                        logger.debug(' - CREATE VAR %s %s %s' % (var_num, item['name'], item['name_translations']))
                        test_variable_type = TestVariableType.with_context(lang=DEFAULT_LANG).create({
                            'spreadsheet': self.id,
                            'test_type': test_type.id,
                            'num': var_num,
                            'name': item['name'],
                        })
                    # Translations
                    for lang, value in item['name_translations'].items():
                        logger.debug('TEST VARIABLE TRANSLATION %s: %s' % (lang, value))
                        test_variable_type.with_context(lang=lang).write({
                            'name': value,
                        })

        def save_test_type(current_test):
            logger.debug('PROCESSING TEST %s' % (current_test))
            default_code = current_test.get('terralab.test_name', {}).get('value', None)
            if not default_code:
                raise ValidationError('Test Name Missing')
            existing_test_types = TestType.search([('spreadsheet', '=', self.id), ('default_code', '=', default_code)])
            uom_name = ''
            uom_name_obj = current_test.get('terralab.test_result_uom')
            name_translations = current_test.get('terralab.test_name', {}).get('name_translations', {})
            if uom_name_obj and uom_name_obj.get('value'):
                uom_name = uom_name_obj['value']
            if len(existing_test_types) <= 0:
                logger.debug('CREATE TEST %s' % (current_test))
                test_type = TestType.with_context(lang=DEFAULT_LANG).create({
                    'default_code': default_code,
                    'name': name_translations['en_US'],
                    'spreadsheet': self.id,
                    'test_result_uom_name': uom_name,
                })
            else:
                test_type = existing_test_types[0]
                logger.debug('UPDATE TEST %s' % (test_type))
                test_type.with_context(lang=DEFAULT_LANG).write({
                    'name': name_translations['en_US'],
                    'test_result_uom_name': uom_name,
                })
            # Test name Translations
            logger.debug('Test name translations: %s' % (name_translations))
            for lang, value in name_translations.items():
                logger.debug('TEST NAME TRANSLATION %s: %s' % (lang, value))
                test_type.with_context(lang=lang).write({
                    'name': value,
                })

            save_test_variables(test_type, current_test)

        for row in rows[1:]:
            field = str(row[col_mapping['Field']] if col_mapping['Field'] < len(row) else '')
            value = row[col_mapping['Values']] if col_mapping['Values'] < len(row) else None
            name = row[col_mapping['Name en_US']] if col_mapping['Name en_US'] < len(row) else None
            name_translations = {}
            for nkey, col_num in col_mapping.items():
                key = str(nkey)
                if key.startswith('Name '):
                    lang = key[5:]
                    name_value = row[col_num] if col_num < len(row) else None
                    #logger.debug('TRANSLATION %s %s %s' % (field, lang, name_value))
                    name_translations[lang] = name_value
            if field == 'terralab.test_name':
                # Start new test definition
                if len(current_test.keys()) > 0:
                    save_test_type(current_test)
                current_test = {}
            if field and field[0] != '#':
                current_test[field] = {
                    'value': value,
                    'name': name,
                    'name_translations': name_translations,
                }
        if len(current_test.keys()) > 0:
            save_test_type(current_test)
