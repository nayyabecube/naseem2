# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.osv import osv
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
import datetime
from datetime import datetime,date,timedelta,time
import dateutil.parser
from dateutil.relativedelta import relativedelta
from itertools import groupby
import collections
from collections import namedtuple
import json
import time
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError

class JornalEntriesCustomization(models.Model):
	_inherit = 'account.move'
	bank_transfer_id = fields.Many2one('bank.transfer.cheque',string="Bank Transfer ID")
	bank_adjustments_id = fields.Many2one('bank.adjustments.cheque',string="Bank Transfer ID")
	supplier_adjustments_id = fields.Many2one('supplier.adjustments',string="Supplier Adjustment ID")


	@api.model
	def create(self, vals):	
		new_record = super(JornalEntriesCustomization, self).create(vals)
		if new_record.line_ids:
			debit = 0
			credit = 0
			for x in new_record.line_ids:
				debit = debit + x.debit
				credit = credit + x.credit
			if debit != credit:
				raise ValidationError('Debit is not equal to Credit')
		return new_record

	@api.multi
	def write(self, vals):
		res =super(JornalEntriesCustomization, self).write(vals)
		if self.line_ids:
			debit = 0
			credit = 0
			for x in self.line_ids:
				debit = debit + x.debit
				credit = credit + x.credit
			if debit != credit:
				raise ValidationError('Debit is not equal to Credit')
		return res


class JornalEntryLineCustomization(models.Model):
	_inherit = 'account.move.line'
	fc_amount = fields.Float(string="FC Amount ")
	@api.model
	def _getUserShowAccount(self):
		return [('account_show', '=',  self.env.user.show_all_accounts)]
	account_id =  fields.Many2one('account.account',string="Account", domain=_getUserShowAccount)

