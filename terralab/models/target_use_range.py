# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ # type: ignore
import logging

logger = logging.getLogger(__name__)

class TargetUseRange(models.Model):
    _name = 'terralab.targetuserange'
    _inherit = ['mail.thread']
    _description = 'TerraLab Target Use Range'

    spreadsheet = fields.Many2one('terralab.spreadsheet', 'Spreadsheet', track_visibility='onchange') # Spreadsheet source of import
    target_use = fields.Many2one('terralab.targetuse', 'Target Use', track_visibility='onchange') # Target Use Range is of a Target Use
    submitted_samples = fields.Many2many('terralab.submittedsample', track_visibility='onchange') # There are many Target Use Ranges for many Submitted Samples
    test_type = fields.Many2one('terralab.testtype', 'Test Type', track_visibility='onchange') # Target Use Range is connected to a Test Type
    threshold_1 = fields.Float(track_visibility='onchange')
    threshold_2 = fields.Float(track_visibility='onchange')
    threshold_3 = fields.Float(track_visibility='onchange')
    threshold_4 = fields.Float(track_visibility='onchange')
    threshold_5 = fields.Float(track_visibility='onchange')
    name = fields.Char(compute='_get_name', store=True, translate=True, track_visibility='onchange')
    num_thresholds = fields.Integer(track_visibility='onchange')

    @api.depends('target_use', 'test_type')
    def _get_name(self):
        for item in self:
            if item.target_use and item.test_type:
                item.name = '%s (%s)' % (item.target_use.name, item.test_type.name)
            else:
                item.name = ''
