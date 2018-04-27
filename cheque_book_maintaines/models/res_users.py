# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    show_all_accounts = fields.Boolean(string="Show All Accounts")