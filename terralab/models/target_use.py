# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ # type: ignore
import logging

logger = logging.getLogger(__name__)

class TargetUse(models.Model):
    _name = 'terralab.targetuse'
    _inherit = ['mail.thread']
    _description = 'TerraLab Target Use'

    spreadsheet = fields.Many2one('terralab.spreadsheet', 'Spreadsheet', track_visibility='onchange') # Spreadsheet source of import
    target_use_ranges = fields.One2many('terralab.targetuserange', 'target_use', 'Target Use Ranges', track_visibility='onchange')
    default_code = fields.Char(track_visibility='onchange')
    name = fields.Char(translate=True, track_visibility='onchange')
