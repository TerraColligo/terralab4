# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ # type: ignore
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Extend Odoo Order Line to link to TerraLab tests.
# By default, the order line is linked to the Order and to the Test Products.
# We add a link to the Submitted Sample that generated the Order Line.
class OrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['sale.order.line']
    terralab_submitted_sample = fields.Many2one('terralab.submittedsample', 'Submitted Sample', track_visibility='onchange') # An Order Line is attached to a specific Submitted Sample
    terralab_submitted_tests = fields.One2many('terralab.submittedtest', 'order_line', 'Submitted Tests', track_visibility='onchange') # An Order Line is attached to multiple Submitted Tests

# Extend Odoo Order
class Order(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'mail.thread']
    terralab_status = fields.Selection([
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('calculated', _('Calculated')),
        ('validated', _('Validated')),
        ('completed', _('Completed')),
    ], string='TerraLab Status', default=None, track_visibility='onchange')
    terralab_draft_date = fields.Datetime(string='Draft Date', readonly=True, track_visibility='onchange')
    terralab_submitted_date = fields.Datetime(string='Submitted Date', readonly=True, track_visibility='onchange')
    terralab_accepted_date = fields.Datetime(string='Accepted Date', readonly=True, track_visibility='onchange')
    terralab_rejected_date = fields.Datetime(string='Rejected Date', readonly=True)
    terralab_calculated_date = fields.Datetime(string='Calculated Date', readonly=True, track_visibility='onchange')
    terralab_validated_date = fields.Datetime(string='Validated Date', readonly=True, track_visibility='onchange')
    terralab_completed_date = fields.Datetime(string='Completed Date', readonly=True, track_visibility='onchange')

    # Samples
    terralab_submitted_samples = fields.One2many('terralab.submittedsample', 'order', 'TerraLab Samples', track_visibility='onchange') # All Samples Submitted to this Order
    terralab_submitted_samples_count = fields.Integer(compute='_compute_submitted_samples_count', store=True)

    # Tests
    terralab_submitted_tests = fields.One2many('terralab.submittedtest', 'order', 'TerraLab Tests', track_visibility='onchange') # All Tests Submitted to this Order
    terralab_submitted_tests_count = fields.Integer(compute='_compute_submitted_tests_count', store=True)

    # Test Variables
    terralab_submitted_test_variables = fields.One2many('terralab.submittedtestvariable', 'order', 'TerraLab Test Variables', track_visibility='onchange') # All Test Variables Submitted to this Order
    terralab_submitted_test_variables_count = fields.Integer(compute='_compute_submitted_test_variables_count', store=True)

    # Other
    terralab_next_action = fields.Char(compute='_compute_terralab_next_action', store=True, track_visibility='onchange') # Next action required
    terralab_report_text_1 = fields.Text()
    terralab_report_text_2 = fields.Text()
    terralab_report_text_3 = fields.Text()
    terralab_report_text_4 = fields.Text()

    @api.depends('terralab_submitted_samples', 'terralab_status', 'terralab_submitted_samples.submitted_tests', 'terralab_submitted_samples.submitted_tests.submitted_test_variables', 'terralab_submitted_samples.submitted_tests.submitted_test_variables.value')
    def _compute_terralab_next_action(self):
        for item in self:
            logger.debug('CALCULATING NEXT TERRALAB ACTION FOR ITEM %s' % (item))
            item.terralab_next_action = item.compute_terralab_next_action(item.terralab_status)

    @api.depends('terralab_submitted_samples')
    def _compute_submitted_samples_count(self):
        for item in self:
            submitted_samples_count = 0
            for submitted_sample in item.terralab_submitted_samples:
                submitted_samples_count += 1
            item.terralab_submitted_samples_count = submitted_samples_count

    @api.depends('terralab_submitted_tests')
    def _compute_submitted_tests_count(self):
        for item in self:
            submitted_tests_count = 0
            for submitted_test in item.terralab_submitted_tests:
                submitted_tests_count += 1
            item.terralab_submitted_tests_count = submitted_tests_count

    @api.depends('terralab_submitted_test_variables')
    def _compute_submitted_test_variables_count(self):
        for item in self:
            submitted_test_variables_count = 0
            for submitted_test_variable in item.terralab_submitted_test_variables:
                submitted_test_variables_count += 1
            item.terralab_submitted_test_variables_count = submitted_test_variables_count

    def compute_terralab_next_action(self, order_terralab_status):
        logger.debug('COMPUTING NEXT TERRALAB ACTION FOR %s %s' % (self, order_terralab_status))
        if len(self.terralab_submitted_samples) <= 0:
            return _('Add at least one submitted sample')
        for submitted_sample in self.terralab_submitted_samples:
            required_action = submitted_sample.compute_terralab_next_action(order_terralab_status)
            if required_action:
                return required_action
        # XXX TODO We should check if any tests in attached products are missing submitted samples
        # No required action found; check status
        if self.terralab_status == 'draft':
            # Order should be submitted
            return _('Submit order')
        elif self.terralab_status == 'submitted':
            # Order should be accepted
            return _('Accept or reject order')
        elif self.terralab_status == 'accepted':
            # Order should be calculated
            return _('Calculate test results')
        elif self.terralab_status == 'calculated':
            # Order should be validated
            return _('Validate test results')
        elif self.terralab_status == 'validated':
            # Order should be completed
            return _('Complete order')
        return ''

    # Create Order Line for the specified Test Product related to the specified Submitted Sample
    # Returns tuple with the order line, number of created order lines, tests, test variables created
    def _add_terralab_test_product_order_line(self, submitted_sample, test_product, auto_add_order_lines, is_bom) -> (models.Model, int, int, int):
        OrderLine = self.env['sale.order.line']
        SubmittedTest = self.env['terralab.submittedtest']
        SubmittedTestVariable = self.env['terralab.submittedtestvariable']

        # Do we already have an order line for this test product in this order?
        order_line = None
        num_created_order_lines = 0
        num_created_tests = 0
        num_created_test_variables = 0

        logger.info('Finding order line for product %s' % (test_product.id))
        for existing_order_line in self.order_line:
            if existing_order_line.product_id.id == test_product.id and existing_order_line.terralab_submitted_sample and existing_order_line.terralab_submitted_sample.id == submitted_sample.id:
                logger.info(' - Found existing order line %s %s %s' % (existing_order_line, existing_order_line.product_id.id, existing_order_line.product_template_id.id))
                order_line = existing_order_line
            #else:
            #    logger.info(' - Non matching order line %s %s %s' % (existing_order_line, existing_order_line.product_id.id, existing_order_line.product_template_id.id))
        if not order_line and auto_add_order_lines:
            # Create order line
            order_line = OrderLine.create({
                'order_id': self.id,
                'product_id': test_product.id,
                'name': test_product.name,
                'product_uom': test_product.uom_id.id if test_product.uom_id else None,
                'terralab_submitted_sample': submitted_sample.id,
            })
            order_line.product_id_change()
            num_created_order_lines += 1
        # Okay, now we have an order line. Create Submitted Tests for each Test Type.
        for test_type in test_product.terralab_test_types:
            # Do we already have a Submitted Test for this Test Type?
            submitted_test = None
            for existing_submitted_test in self.terralab_submitted_tests:
                if existing_submitted_test.test_type and existing_submitted_test.test_type.id == test_type.id and existing_submitted_test.submitted_sample.id == submitted_sample.id:
                    submitted_test = existing_submitted_test
            if not submitted_test:
                # Create Submitted Test
                submitted_test = SubmittedTest.create({
                    'test_type': test_type.id,
                    'order': self.id,
                    'order_line': order_line.id if order_line else None,
                    'submitted_sample': submitted_sample.id,
                    'test_result_uom_name': test_type.test_result_uom_name,
                })
                num_created_tests += 1

            # Create Submitted Test Variables for the Submitted Test
            for test_variable_type in test_type.test_variable_types:
                submitted_test_variable = None
                for existing_submitted_test_variable in submitted_test.submitted_test_variables:
                    if existing_submitted_test_variable.test_variable_type.id == test_variable_type.id and \
                        existing_submitted_test_variable.order.id == self.id and \
                        existing_submitted_test_variable.submitted_sample.id == submitted_sample.id and \
                        existing_submitted_test_variable.submitted_test.id == submitted_test.id:
                            submitted_test_variable = existing_submitted_test_variable
                if not submitted_test_variable:
                    logger.info('Creating Submitted Test Variable for Test Variable Type: %s' % (test_variable_type))
                    submitted_test_variable = SubmittedTestVariable.create({
                        'test_variable_type': test_variable_type.id,
                        'order': self.id,
                        'submitted_sample': submitted_sample.id,
                        'submitted_test': submitted_test.id,
                    })
                    num_created_test_variables += 1

        return order_line, num_created_order_lines, num_created_tests, num_created_test_variables

    def _create_order_lines_for_test_types(self, auto_add_order_lines):
        # Create Order Lines for all Submitted Samples

        all_order_lines: List[models.Model] = []
        total_num_created_order_lines = 0
        total_num_created_tests = 0
        total_num_created_test_variables = 0

        for submitted_sample in self.terralab_submitted_samples:
            logger.info('Checking Order Submitted Sample %s' % (submitted_sample))
            # Create OrderLines for all Test Products
            for test_product in submitted_sample.test_products:
                logger.info('Checking Order Sample Test Product %s' % (test_product))

                # Direct tests
                if hasattr(test_product, 'terralab_test_types') and len(test_product.terralab_test_types) > 0:
                    order_line, num_created_order_lines, num_created_tests, num_created_test_variables = self._add_terralab_test_product_order_line(submitted_sample, test_product, auto_add_order_lines, False)
                    all_order_lines.append(order_line)
                    total_num_created_order_lines += num_created_order_lines
                    total_num_created_tests += num_created_tests
                    total_num_created_test_variables += num_created_test_variables

                # BoM tests
                if hasattr(test_product, 'bom_ids'):
                    for bom_id in test_product.bom_ids:
                        if hasattr(bom_id, 'bom_line_ids'):
                            for bom_line_id in bom_id.bom_line_ids:
                                if bom_line_id.product_id and hasattr(bom_line_id.product_id, 'terralab_test_types') and len(bom_line_id.product_id.terralab_test_types) > 0:
                                    order_line, num_created_order_lines, num_created_tests, num_created_test_variables = self._add_terralab_test_product_order_line(submitted_sample, test_product, auto_add_order_lines, True)
                                    all_order_lines.append(order_line)
                                    total_num_created_order_lines += num_created_order_lines
                                    total_num_created_tests += num_created_tests
                                    total_num_created_test_variables += num_created_test_variables

        logger.info('TerraLab added %s order line(s) with %s test(s) and %s test variable(s) to order %s %s.' % (total_num_created_order_lines, total_num_created_tests, total_num_created_test_variables, self.name, self))
        if total_num_created_order_lines > 0:
            # Show notification
            self.message_post(body=_('TerraLab added %s order line(s) with %s test(s) and %s test variable(s) to this order.') % (total_num_created_order_lines, total_num_created_tests, total_num_created_test_variables))

    def _set_terralab_status_date(self, values, old_status):
        new_status = values.get('terralab_status', '')
        if new_status != old_status:
            if new_status == 'draft':
                values['terralab_draft_date'] = fields.Datetime.now()
            if new_status == 'submitted':
                values['terralab_submitted_date'] = fields.Datetime.now()
            if new_status == 'accepted':
                values['terralab_accepted_date'] = fields.Datetime.now()
            if new_status == 'rejected':
                values['terralab_rejected_date'] = fields.Datetime.now()
            if new_status == 'calculated':
                values['terralab_calculated_date'] = fields.Datetime.now()
            if new_status == 'validated':
                values['terralab_validated_date'] = fields.Datetime.now()
            if new_status == 'completed':
                values['terralab_completed_date'] = fields.Datetime.now()

    @api.model
    def create(self, values):
        logger.debug('ORDER CREATE: %s' % (self))
        # If any TerraLab Submitted Samples are included in the order, set the TerraLab status to Draft so it appears in lists
        if len(values.get('terralab_submitted_samples', [])) > 0 and not values.get('terralab_status', ''):
            logger.debug('Created Order contains TerraLab Submitted Samples, setting status to draft')
            values['terralab_status'] = 'draft'
            values['terralab_draft_date'] = fields.Date.to_string(datetime.now())
        self._set_terralab_status_date(values, '')
        order = super(Order, self).create(values)
        logger.debug('ORDER CREATED: %s' % (order))
        auto_add_order_lines = (order.state == 'draft' or order.state == 'sent')
        order._create_order_lines_for_test_types(auto_add_order_lines)
        logger.debug('ORDER CREATE FINISHED: %s' % (order))
        return order

    def write(self, values):
        logger.debug('ORDER WRITE: %s' % (self))
        self._set_terralab_status_date(values, self.terralab_status)
        super(Order, self).write(values)
        auto_add_order_lines = (self.state == 'draft' or self.state == 'sent')
        self._create_order_lines_for_test_types(auto_add_order_lines)
        # If TerraLab stauts it not set yet, check if order contains TerraLab tests and set to draft
        if not self.terralab_status:
            is_terralab_order = False
            for order_line in self.order_line:
                if len(order_line.product_id.terralab_test_types) > 0:
                    is_terralab_order = True
            if is_terralab_order:
                # Default order to draft status
                super(Order, self).write({
                    'terralab_status': 'draft',
                    'terralab_draft_date': fields.Date.to_string(datetime.now()),
                })
        return True

    # Order form action: Mark order TerraLab status as submitted
    def action_terralab_submit(self):
        self.write({
            'terralab_status': 'submitted',
        })
#        return {
#            'effect': {
#                'fadeout': 'slow',
#                'message': _('TerraLab order status is now Submitted.'),
#                'type': 'rainbow_man',
#            }
#        }

    # Order form action: Mark order TerraLab status as draft
    def action_terralab_draft(self):
        self.write({
            'terralab_status': 'draft',
        })
#        return {
#            'effect': {
#                'fadeout': 'slow',
#                'message': _('TerraLab order status is now Draft.'),
#                'type': 'rainbow_man',
#            }
#        }

    # Order form action: Mark order TerraLab status as accepted
    def action_terralab_accept(self):
        self.write({
            'terralab_status': 'accepted',
        })
#        return {
#            'effect': {
#                'fadeout': 'slow',
#                'message': _('TerraLab order status is now Accepted.'),
#                'type': 'rainbow_man',
#            }
#        }

    # Order form action: Mark order TerraLab status as rejected
    def action_terralab_reject(self):
        self.write({
            'terralab_status': 'rejected',
        })
#        return {
#            'effect': {
#                'fadeout': 'slow',
#                'message': _('TerraLab order status is now Rejected.'),
#                'type': 'rainbow_man',
#            }
#        }

    # Order form action: Calculate test results
    def action_terralab_calculate(self):
        self.calculate_all_test_results()
        self.write({
            'terralab_status': 'calculated',
        })
#        return {
#            'effect': {
#                'fadeout': 'slow',
#                'message': _('Results calculated successfully.'),
#                'type': 'rainbow_man',
#            }
#        }

    # Order form action: Mark order TerraLab status as validated
    def action_terralab_validate(self):
        self.write({
            'terralab_status': 'validated',
        })
#        return {
#            'effect': {
#                'fadeout': 'slow',
#                'message': _('TerraLab order status is now Validated.'),
#                'type': 'rainbow_man',
#            }
#        }

    # Order form action: Mark order TerraLab status as calculated
    def action_terralab_invalidate(self):
        self.write({
            'terralab_status': 'calculated',
        })
#        return {
#            'effect': {
#                'fadeout': 'slow',
#                'message': _('TerraLab order status is now Invalidated.'),
#                'type': 'rainbow_man',
#            }
#        }

    # Order form action: Mark order TerraLab status as complete
    def action_terralab_complete(self):
        self.write({
            'terralab_status': 'completed',
        })
#        return {
#            'effect': {
#                'fadeout': 'slow',
#                'message': _('TerraLab order status is now Completed.'),
#                'type': 'rainbow_man',
#            }
#        }

    # Calculate test results using spreadsheet
    def calculate_all_test_results(self):
        for order in self:
            for submitted_sample in order.terralab_submitted_samples:
                for submitted_test in submitted_sample.submitted_tests:
                    submitted_test.calculate_test_result()
