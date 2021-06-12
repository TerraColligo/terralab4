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
from googleapiclient.discovery import build # type: ignore
import google.oauth2.credentials # type: ignore
import re
from .import_all import get_google_spreadsheets

PartnerMapping = Dict[str, OdooModel]
CurrentOrder = Dict[str, Any]

logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_LANG = 'en_US'

# This parent class implements Spreadsheet importing.
class SpreadsheetGenerateDemoOrders(object):
    def action_generate_demo_orders(self: OdooModel) -> OdooActionResponse:
        access_token = self.env['google.drive.config'].get_access_token(scope='https://spreadsheets.google.com/feeds')
        spreadsheets = get_google_spreadsheets(access_token)
        logger.info('Importing tests from spreadsheet %s' % (self.spreadsheet_id))
        # The ranges that we'll read in one batch operation
        ranges = ['Demodata!A:ZZ']
        value_batches = spreadsheets.values().batchGet(spreadsheetId=self.spreadsheet_id, ranges=ranges).execute()
        value_ranges = value_batches['valueRanges']
        demodata_range = value_ranges[0]
        partner_mapping = self.import_demo_partners(demodata_range['values'])
        self.import_demo_orders(demodata_range['values'], partner_mapping)
        self.message_post(body=_('TerraLab generated spreadsheet demo orders successfully.'))
        return {
            'effect': {
                'fadeout': 'slow',
                'message': _('Demo orders generated successfully.'),
                'type': 'rainbow_man',
            }
        }

    def import_demo_partners(self: OdooModel, rows: SpreadsheetRows) -> PartnerMapping:
        Partner = self.env['res.partner']
        col_mapping = {}
        partner_mapping: PartnerMapping = {}
        for index, col in enumerate(rows[0]):
            col_mapping[col] = index
        for row in rows[1:]:
            if col_mapping['res.partner.name'] < len(row) and col_mapping['res.partner.email'] < len(row):
                partner_name: str = str(row[col_mapping['res.partner.name']])
                partner_email: str = str(row[col_mapping['res.partner.email']])
                partner_lang: str = str(row[col_mapping['res.partner.lang']])
                if partner_name and partner_email:
                    existing_partners = Partner.search([('email', '=', partner_email)])
                    if len(existing_partners) > 0:
                        logger.info('EXISTING DEMO PARTNER: %s (%s)' % (partner_email, partner_name))
                        existing_partners[0].write({
                            'name': partner_name,
                            'is_company': True,
                            'lang': partner_lang,
                        })
                        partner = existing_partners[0]
                    else:
                        logger.info('ADD DEMO PARTNER: %s (%s)' % (partner_email, partner_name))
                        partner = Partner.create({
                            'email': partner_email,
                            'name': partner_name,
                            'is_company': True,
                            'lang': partner_lang,
                        })
                    partner_mapping[partner_email] = partner
        return partner_mapping

    def import_demo_orders(self: OdooModel, rows: SpreadsheetRows, partner_mapping: PartnerMapping) -> None:
        Order = self.env['sale.order']
        TestProduct = self.env['product.template']
        SampleType = self.env['terralab.sampletype']
        SubmittedSample = self.env['terralab.submittedsample']
        TargetUse = self.env['terralab.targetuse']
        TargetUseRange = self.env['terralab.targetuserange']
        TestType = self.env['terralab.testtype']
        SubmittedTest = self.env['terralab.submittedtest']
        logger.info('Importing %s demo order row(s)' % (len(rows)))
        col_mapping: SpreadsheetColMapping = {}
        current_order: CurrentOrder = {}
        for index, col in enumerate(rows[0]):
            col_mapping[str(col)] = index
        logger.debug('Demo order column mapping: %s' % (col_mapping))

        def save_order(current_order: CurrentOrder, row_num: int):
            #logger.info('CREATE DEMO ORDER: %s' % (current_order))
            target_uses: List[OdooModel] = TargetUse.search([('default_code', '=', current_order['terralab.submittedsample.submitted_target_use'])])
            if len(target_uses) <= 0:
                raise ValidationError('Target Use not found: %s' % (current_order['terralab.submittedsample.submitted_target_use']))
            target_use = target_uses[0]
            existing_sample_types: List[OdooModel] = SampleType.search([('default_code', '=', current_order['terralab.submittedsample.sample_type'])])
            sample_type = existing_sample_types[0]
            logger.info('- TARGET USE %s %s %s' % (target_use, target_use.default_code, target_use.name))

            test_product_ids: List[int] = []
            target_use_range_ids = []
            test_product_map: Dict[int, str] = {}
            for test_product_code, values in current_order['test_products'].items():
                existing_test_products = TestProduct.search([('default_code', '=', test_product_code)])
                if len(existing_test_products) <= 0:
                    raise ValidationError('Product not found: %s (line %d)' % (test_product_code, row_num))
                test_product = existing_test_products[0]
                test_product_ids.append(test_product.id)
                test_product_map[test_product.id] = test_product_code
                logger.info('- TEST PRODUCT %s (%s)' % (test_product_code, test_product.id))
                for test_name, test_variables in values['tests'].items():
                    logger.info('  - TEST %s %s' % (test_name, test_variables))
                    existing_target_use_ranges = TargetUseRange.search([('target_use', '=', target_use.id), ('test_type.default_code', '=', test_name)])
                    if len(existing_target_use_ranges) > 0:
                        target_use_range = existing_target_use_ranges[0]
                        logger.info('    - TARGET USE RANGE %s' % (target_use_range))
                        # Attach this target use range to the Submitted sample
                        target_use_range_ids.append(target_use_range.id)

            submitted_sample = SubmittedSample.create({
                #'order': order.id,
                'sample_type': sample_type.id,
                'name': current_order['terralab.submittedsample.name'],
                'sample_id': current_order['terralab.submittedsample.sample_id'],
                'serial_number': current_order['terralab.submittedsample.serial_number'],
                'deadline': current_order['terralab.submittedsample.deadline'].replace('T', ' '),
                'area': current_order['terralab.submittedsample.area'],
                'volume': current_order['terralab.submittedsample.volume'],
                'location': current_order['terralab.submittedsample.location'],
                'target_use_ranges': target_use_range_ids,
                'test_products': test_product_ids,
            })

            partner = partner_mapping.get(current_order['res.partner.email'], None)
            if not partner:
                raise ValidationError('Partner Not Found: %s (line %d)' % (current_order['res.partner.email'], row_num))

            order = Order.create({
                'partner_id': partner.id,
                'terralab_submitted_samples': [submitted_sample.id],
                'terralab_report_text_1': current_order['report_field_1'],
                'terralab_report_text_2': current_order['report_field_2'],
                'terralab_report_text_3': current_order['report_field_3'],
                'terralab_report_text_4': current_order['report_field_4'],
            })

            submitted_sample.write({
                'order': order.id,
            })

            logger.info('CONFIGURING TEST VARIABLES...')
            logger.info('TEST PRODUCT MAP %s' % (test_product_map))
            for order_line in order.order_line:
                logger.info('- ORDER LINE %s product %s template %s' % (order_line, order_line.product_id, order_line.product_template_id))
                test_product_code = test_product_map.get(order_line.product_template_id.id, '')
                if not test_product_code:
                    logger.info('     - TEST PRODUCT NOT FOUND: %s' % (order_line.product_template_id))
                else:
                    tests = current_order['test_products'][test_product_code]['tests']
                    for terralab_submitted_test in order_line.terralab_submitted_tests:
                        test_variables = tests[terralab_submitted_test.test_type.default_code]
                        logger.info('  - TEST %s %s %s VARIABLES %s' % (terralab_submitted_test, terralab_submitted_test.test_type.default_code, terralab_submitted_test.test_type.name, test_variables))
                        for submitted_test_variable in terralab_submitted_test.submitted_test_variables:
                            # Do we have a value for this variable?
                            if submitted_test_variable.num - 1 < len(test_variables):
                                test_variable_value = test_variables[submitted_test_variable.num - 1]
                                logger.info('     - VAR %s %s => %s' % (submitted_test_variable, submitted_test_variable.num, test_variable_value))
                                submitted_test_variable.write({
                                    'value': test_variable_value,
                                })
                            else:
                                logger.info('     - VAR %s %s NOT FOUND IN %s' % (submitted_test_variable, submitted_test_variable.num, test_variables))

        current_product: str = ''
        row_num = 0
        for row in rows[1:]:
            row_num += 1
            sample_type_default_code = row[col_mapping['terralab.submittedsample.sample_type']]
            test_variables = [
                row[col_mapping['v_1']] if col_mapping['v_1'] < len(row) else '',
                row[col_mapping['v_2']] if col_mapping['v_2'] < len(row) else '',
                row[col_mapping['v_3']] if col_mapping['v_3'] < len(row) else '',
                row[col_mapping['v_4']] if col_mapping['v_4'] < len(row) else '',
                row[col_mapping['v_5']] if col_mapping['v_5'] < len(row) else '',
                row[col_mapping['v_6']] if col_mapping['v_6'] < len(row) else '',
                row[col_mapping['v_7']] if col_mapping['v_7'] < len(row) else '',
                row[col_mapping['v_8']] if col_mapping['v_8'] < len(row) else '',
                row[col_mapping['v_9']] if col_mapping['v_9'] < len(row) else '',
                row[col_mapping['v_10']] if col_mapping['v_10'] < len(row) else '',
            ]
            if sample_type_default_code:
                if len(current_order) > 0:
                    save_order(current_order, row_num)
                current_product = str(row[col_mapping['terralab.submittedsample.test_products']])
                current_test: str = str(row[col_mapping['sale.order.terralab_submitted_tests.test_name']])
                previous_partner_email: str = current_order.get('res.partner.email', '')
                current_order = {
                    'test_products': {
                        current_product: {
                            'tests': {
                                current_test: test_variables,
                            },
                        },
                    },
                }
                for col_name, col_num in col_mapping.items():
                    current_order[col_name] = row[col_num] if col_num < len(row) else ''
                if not current_order['res.partner.email']:
                    # Use previous
                    current_order['res.partner.email'] = previous_partner_email
            elif current_product:
                # Adding products to the order

                if col_mapping['terralab.submittedsample.test_products'] < len(row) and row[col_mapping['terralab.submittedsample.test_products']]:
                    current_product = str(row[col_mapping['terralab.submittedsample.test_products']])
                    #logger.info('Start new product: %s' % (current_product))
                    current_order['test_products'][current_product] = {
                        'tests': {},
                    }

                # Adding tests and variables to the order
                if col_mapping['sale.order.terralab_submitted_tests.test_name'] < len(row) and row[col_mapping['sale.order.terralab_submitted_tests.test_name']]:
                    current_test = str(row[col_mapping['sale.order.terralab_submitted_tests.test_name']])
                    #logger.info('Start new test: %s' % (current_test))
                    current_order['test_products'][current_product]['tests'][current_test] = test_variables

        if len(current_order) > 0:
            save_order(current_order, row_num)
