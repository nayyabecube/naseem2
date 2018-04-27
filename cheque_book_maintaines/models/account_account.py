# -*- coding: utf-8 -*-

from openerp import models, fields, api

class CharofAccounts(models.Model):
    _inherit = 'account.account'
    account_show = fields.Boolean(string="Show Account")
    bank = fields.Boolean(string="Bank")
    cash = fields.Boolean(string="Cash")