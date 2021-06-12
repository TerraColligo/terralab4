# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ # type: ignore
import logging

logger = logging.getLogger(__name__)

class SubmittedTest(models.Model):
    _name = 'terralab.submittedtest'
    _inherit = ['mail.thread']
    _description = 'TerraLab Submitted Test'
    _order = 'sample_group desc,test_type_name asc'

    test_type = fields.Many2one('terralab.testtype', 'Test Type', track_visibility='onchange') # A Submitted Test is a specific Test Type
    test_type_name = fields.Char(related='test_type.name', store=True)
    order = fields.Many2one('sale.order', 'Order', track_visibility='onchange') # Submitted Test is always attached to an Order
    order_line = fields.Many2one('sale.order.line', 'Order Line', track_visibility='onchange') # Submitted Test is automatically attached to an Order Line when creating or updating order
    order_name = fields.Char(related='order.name', store=True, track_visibility='onchange')
    order_partner_name = fields.Char(related='order.partner_id.name', store=True, track_visibility='onchange')
    order_date = fields.Datetime(related='order.date_order', store=True, track_visibility='onchange')
    order_terralab_status = fields.Selection([
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('calculated', _('Calculated')),
        ('validated', _('Validated')),
        ('completed', _('Completed')),
    ], string='TerraLab Status', default=None, related='order.terralab_status', store=True)
    sample_group = fields.Char(compute='_get_sample_group', store=True, track_visibility='onchange')
    submitted_sample = fields.Many2one('terralab.submittedsample', 'Submitted Sample', track_visibility='onchange') # A Submitted Test is attached to a specific Submitted Sample
    submitted_sample_name = fields.Char(related='submitted_sample.name', store=True, track_visibility='onchange')
    submitted_sample_id = fields.Char(related='submitted_sample.sample_id', store=True, track_visibility='onchange')
    submitted_sample_serial_number = fields.Char(related='submitted_sample.serial_number', store=True, track_visibility='onchange')
    submitted_sample_receive_date = fields.Datetime(related='submitted_sample.receive_date', store=True, track_visibility='onchange')
    submitted_sample_deadline = fields.Datetime(related='submitted_sample.deadline', store=True, track_visibility='onchange')
    submitted_sample_create_date = fields.Datetime(related='submitted_sample.create_date', store=True, track_visibility='onchange')
    submitted_test_variables = fields.One2many('terralab.submittedtestvariable', 'submitted_test', 'Submitted Test Variables', track_visibility='onchange') # A Submitted Test has a number of Submitted Test Variables
    test_result = fields.Char(track_visibility='onchange')
    test_result_uom_name = fields.Char(track_visibility='onchange')
    var_1 = fields.Many2one('terralab.submittedtestvariable', 'Var 1', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_1_type = fields.Many2one('terralab.testvariabletype', 'Type 1', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_1_value = fields.Char('Value 1', compute='_get_variable_fields', inverse='_set_variable_value_1', store=True, track_visibility='onchange')
    var_2 = fields.Many2one('terralab.submittedtestvariable', 'Var 2', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_2_type = fields.Many2one('terralab.testvariabletype', 'Type 2', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_2_value = fields.Char('Value 2', compute='_get_variable_fields', inverse='_set_variable_value_2', store=True, track_visibility='onchange')
    var_3 = fields.Many2one('terralab.submittedtestvariable', 'Var 3', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_3_type = fields.Many2one('terralab.testvariabletype', 'Type 3', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_3_value = fields.Char('Value 3', compute='_get_variable_fields', inverse='_set_variable_value_3', store=True, track_visibility='onchange')
    var_4 = fields.Many2one('terralab.submittedtestvariable', 'Var 4', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_4_type = fields.Many2one('terralab.testvariabletype', 'Type 4', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_4_value = fields.Char('Value 4', compute='_get_variable_fields', inverse='_set_variable_value_4', store=True, track_visibility='onchange')
    var_5 = fields.Many2one('terralab.submittedtestvariable', 'Var 5', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_5_type = fields.Many2one('terralab.testvariabletype', 'Type 5', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_5_value = fields.Char('Value 5', compute='_get_variable_fields', inverse='_set_variable_value_5', store=True, track_visibility='onchange')
    var_6 = fields.Many2one('terralab.submittedtestvariable', 'Var 6', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_6_type = fields.Many2one('terralab.testvariabletype', 'Type 6', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_6_value = fields.Char('Value 6', compute='_get_variable_fields', inverse='_set_variable_value_6', store=True, track_visibility='onchange')
    var_7 = fields.Many2one('terralab.submittedtestvariable', 'Var 7', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_7_type = fields.Many2one('terralab.testvariabletype', 'Type 7', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_7_value = fields.Char('Value 7', compute='_get_variable_fields', inverse='_set_variable_value_7', store=True, track_visibility='onchange')
    var_7 = fields.Many2one('terralab.submittedtestvariable', 'Var 8', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_8_type = fields.Many2one('terralab.testvariabletype', 'Type 8', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_8_value = fields.Char('Value 8', compute='_get_variable_fields', inverse='_set_variable_value_8', store=True, track_visibility='onchange')
    var_9 = fields.Many2one('terralab.submittedtestvariable', 'Var 9', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_9_type = fields.Many2one('terralab.testvariabletype', 'Type 9', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_9_value = fields.Char('Value 9', compute='_get_variable_fields', inverse='_set_variable_value_9', store=True, track_visibility='onchange')
    var_10 = fields.Many2one('terralab.submittedtestvariable', 'Var 10', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_10_type = fields.Many2one('terralab.testvariabletype', 'Type 10', compute='_get_variable_fields', store=True, track_visibility='onchange')
    var_10_value = fields.Char('Value 10', compute='_get_variable_fields', inverse='_set_variable_value_10',  store=True, track_visibility='onchange')

    def _set_variable_value_1(self): self._set_variable_value(1)
    def _set_variable_value_2(self): self._set_variable_value(2)
    def _set_variable_value_3(self): self._set_variable_value(3)
    def _set_variable_value_4(self): self._set_variable_value(4)
    def _set_variable_value_5(self): self._set_variable_value(5)
    def _set_variable_value_6(self): self._set_variable_value(6)
    def _set_variable_value_7(self): self._set_variable_value(7)
    def _set_variable_value_8(self): self._set_variable_value(8)
    def _set_variable_value_9(self): self._set_variable_value(9)
    def _set_variable_value_10(self): self._set_variable_value(10)

    def _set_variable_value(self, num):
        for item in self:
            if hasattr(item, 'var_%s' % (num)):
                getattr(item, 'var_%s' % (num)).write({ 'value': getattr(item, 'var_%s_value' % (num)) })

    @api.depends('submitted_test_variables')
    def _get_variable_fields(self):
        for item in self:
            for variable in item.submitted_test_variables:
                if 1 <= variable.num and variable.num <= 10:
                    setattr(item, 'var_%s' % (variable.num), variable)
                    setattr(item, 'var_%s_type' % (variable.num), variable.test_variable_type)
                    setattr(item, 'var_%s_value' % (variable.num), variable.value)

    def name_get(self):
        return [(submitted_test.id, '%s %s %s' % (submitted_test.submitted_sample.sample_type.name, (submitted_test.submitted_sample.sample_id or _('(no sample ID)')), submitted_test.test_type.name)) for submitted_test in self]

    @api.depends('order', 'order.terralab_status', 'submitted_sample', 'submitted_sample.sample_type', 'submitted_sample.sample_type.name', 'submitted_sample.sample_id')
    def _get_sample_group(self):
        # This is used for grouping samples in mass-edit
        for item in self:
            item.sample_group = '%s - %s - %s - %s' % (item.order.name if item.order else '(no order)', self.get_selection_label('sale.order', 'terralab_status', item.order.terralab_status) if item.order else '(no order status)', item.submitted_sample.sample_type.name if item.submitted_sample.sample_type else '(no sample type)', item.submitted_sample.sample_id if item.submitted_sample.sample_id else '(no sample ID)')

    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    # Order form action: Calculate test results
    def action_terralab_calculate(self):
        self.calculate_test_result()
        return None

    # What's the next required action for this submitted test?
    def compute_terralab_next_action(self, order_terralab_status):
        if order_terralab_status in ('draft', 'submitted'):
            # In draft or submitted state test variables not yet needed; must accept first
            return ''
        if len(self.submitted_test_variables) <= 0:
            return _('Add submitted test variables for submitted test %s') % (self.name_get()[0][1])
        for submitted_test_variable in self.submitted_test_variables:
            required_action = submitted_test_variable.compute_terralab_next_action(order_terralab_status)
            if required_action:
                return required_action
        # No action required for this test
        return ''

    # Calculate test result
    def calculate_test_result(self):
        spreadsheet = self.test_type.spreadsheet
        result = spreadsheet.calculate_result(self.test_type, self.submitted_test_variables)
        self.write({
            'test_result': result,
        })

    def test_result_float(self):
        try:
            return float(self.test_result)
        except:
            return 0

    def test_result_invalid(self):
        try:
            if self.test_result is False:
                # Null value
                return True
            v = float(self.test_result)
            # Valid float value
            return False
        except:
            return True

    def _message_log(self, *args, **kwargs):
        ret = super(SubmittedTest, self)._message_log(*args, **kwargs)
        logger.info('MESSAGE LOG TEST %s %s %s' % (ret, args, kwargs))

        for item in self:
            if hasattr(item.order, '_message_log'):
                item.order._message_log(*args, **kwargs)

        return ret
