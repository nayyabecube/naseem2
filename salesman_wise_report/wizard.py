#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class SalesmanDetail(models.Model):
	_name = "sales.man"

	date_from = fields.Date("Date From",required=True)
	date_to = fields.Date("Date To",required=True)
	sales_id = fields.Many2many("res.users",string="Salesman")
	sales = fields.Boolean(string="Sales")
	receipts = fields.Boolean(string="Receipts")
	returns = fields.Boolean(string="Returns")
	profit = fields.Boolean(string="Profit")
	b_types = fields.Selection([('all','All'),('specfic', 'Specfic')], string="Filter", required=True)


	@api.onchange('sales')
	def select_SALES(self):
		if self.sales == True:
			self.receipts = False
			self.returns = False
			self.profit = False


	@api.onchange('receipts')
	def select_rece(self):
		if self.receipts == True:
			self.sales = False
			self.returns = False
			self.profit = False


	@api.onchange('returns')
	def select_returns(self):
		if self.returns == True:
			self.sales = False
			self.receipts = False
			self.profit = False

	@api.onchange('profit')
	def select_profit(self):
		if self.profit == True:
			self.sales = False
			self.receipts = False
			self.returns = False

	







	
