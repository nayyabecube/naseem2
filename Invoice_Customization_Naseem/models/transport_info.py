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

class account_bank_extention(models.Model):
	_inherit = 'account.bank.statement.line'

	bilty_link = fields.Many2one('stock.picking',string="stock link")

	# received_by 	= fields.Char(string="Received By")
	# delivered_by 	= fields.Char(string="Delivered By") 
	# bilty_no 		= fields.Char(string="Bilty No.") 
	# origin 			= fields.Char(string="Source Document") 
	# warehouse_id 	= fields.Char(string="WareHouse ID") 


class instant_promo_so(models.Model):
	_name = 'instant.promo.so'

	product_id = fields.Many2one('product.product', string = "Product")
	qty        = fields.Float(string = "Quantity")

	instant_promo_id = fields.Many2one('sale.order')


class transport_info(models.Model):
	_name = 'invoice.payment'

	date          = fields.Date(string="Date")
	pay_id        = fields.Many2one('customer.payment.bcube',string="Payment_id")
	amount    	  = fields.Float(string="Amount")

	pay_tree = fields.Many2one('account.invoice')


class transport_info(models.Model):
	_name = 'epay.wizard'




	# @api.multi
	# def get_epay(self):
	# 	print "checkin ooooooooooooooooooooooooooooooo"



