# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ChkBookBank(models.Model):
    _inherit = 'res.bank'
    custom_acc_no = fields.Char(string="Account No ")