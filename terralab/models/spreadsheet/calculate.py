# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import ValidationError # type: ignore
import logging
from googleapiclient.discovery import build # type: ignore
import google.oauth2.credentials # type: ignore
import re
from .import_all import get_google_spreadsheets

logger = logging.getLogger(__name__)

# This parent class implements Spreadsheet Test Result calculation.
class SpreadsheetCalculate(object):
    def calculate_result(self, test_type, submitted_test_variables):
        access_token = self.env['google.drive.config'].get_access_token(scope='https://spreadsheets.google.com/feeds')
        spreadsheets = get_google_spreadsheets(access_token)
        variable_values = {}
        for submitted_test_variable in submitted_test_variables:
            variable_values[submitted_test_variable.num] = submitted_test_variable.value
        logger.info('Calculating spreadsheet %s test result with variables: %s' % (self.spreadsheet_id, variable_values))
        # Scan the spreadsheet and find the test location, its variable slots and the result slot
        test_values = spreadsheets.values().get(spreadsheetId=self.spreadsheet_id, range='Tests!A:Z').execute()
        test_rows = test_values['values']
        col_mapping = {}
        for index, col in enumerate(test_rows[0]):
            col_mapping[col] = index
        getting_test = False
        row_num = 1
        value_col_letter = chr(ord('A') + col_mapping['Values'])
        variable_refs = {}
        variable_ref_values = {}
        result_ref = None
        for test_row in test_rows[1:]:
            row_num += 1
            field_name = test_row[col_mapping['Field']] if col_mapping['Field'] < len(test_row) else None
            field_value = test_row[col_mapping['Values']] if col_mapping['Values'] < len(test_row) else None
            if field_name == 'terralab.test_name' and field_value == test_type.default_code:
                # Begin test
                logger.info('Found test %s at %s%s' % (field_value, value_col_letter, row_num))
                getting_test = True
            elif field_name == 'terralab.test_name':
                # End test
                getting_test = False
            elif getting_test and field_name:
                if field_name.startswith('terralab.variable_'):
                    var_num = int(field_name[18:])
                    if var_num in variable_values:
                        var_value = variable_values[var_num]
                        var_ref = 'Tests!%s%s' % (value_col_letter, row_num)
                        variable_refs[var_num] = var_ref
                        variable_ref_values[var_ref] = var_value
                        logger.info('Got variable %s slot %s %s %s' % (var_num, var_ref, field_name, field_value))
                elif field_name == 'terralab.test_result':
                    result_ref = 'Tests!%s%s' % (value_col_letter, row_num)
                    logger.info('Got result slot %s %s %s' % (result_ref, field_name, field_value))

        logger.info('Configuring test with result slot %s variable slots %s' % (result_ref, variable_refs))

        # Check that we have all slots
        if not result_ref:
            raise ValidationError('Test Result Slot Not Found')
        for var_num in variable_values.keys():
            if not var_num in variable_refs:
                raise ValidationError('Variable Slot %s Not Found' % (var_num))

        # Update the variables into the sheet
        value_range = []
        for var_ref, var_value in variable_ref_values.items():
            value_range.append({
                'range': var_ref,
                'values': [[var_value]],
            })
        update_response = spreadsheets.values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={'data': value_range, 'valueInputOption': 'USER_ENTERED'}).execute()
        logger.info('Update response: %s' % (update_response))

        # Retrieve result from sheet
        result = spreadsheets.values().get(spreadsheetId=self.spreadsheet_id, range=result_ref).execute()
        values = result.get('values', [])
        logger.info('RESULT VALUE: %s' % (values))
        return values[0][0] if values and len(values) > 0 and values[0] and len(values[0]) > 0 else ''
