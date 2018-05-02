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



class sale_invoice_customized(models.Model):
	_inherit = 'account.invoice'

	due_days = fields.Integer(string="Due Days",compute="compute_remaining_days",store =True)
	date_invoice = fields.Date(required=True, default=fields.Date.context_today, string = "Invoice Date")
	due = fields.Char(string="Due")
	transporter = fields.Many2one('res.partner',string="Transporter")
	incoterm = fields.Many2one('stock.incoterms')
	check_direct_invoice = fields.Boolean('Direct Invoice', default=True)
	remaining_payment_days =fields.Date('Remaining Payment Days')
	reference = fields.Char(string="Reference")
	pay_tree_id = fields.One2many('invoice.payment','pay_tree')
	balance = fields.Float(string="Balance")
	source = fields.Char(string="Source")
	del_records = fields.Many2one('sale.order')
	warehouse = fields.Many2one('stock.warehouse',string="Warehouse")
	stock_id = fields.Many2one('stock.picking',string="Stock Link")
	waveoff_amount 	= fields.Float(string="Discount")
	pdc_module = fields.Many2one('pdc_bcube.pdc_bcube', string="Checks And Balance")
	due_check = fields.Boolean()
	# residual = fields.Monetary(string='Amount Due',
	# 	compute='', store=True, help="Remaining amount due.")
	# residual_signed = fields.Monetary(string='Amount Due in Invoice Currency', currency_field='currency_id',
	# 	compute='', store=True, help="Remaining amount due in the currency of the invoice.")
	# residual_company_signed = fields.Monetary(string='Amount Due in Company Currency', currency_field='company_currency_id',
	# 	compute='', store=True, help="Remaining amount due in the currency of the company.")
	# reconciled = fields.Boolean(string='Paid/Reconciled', store=True, readonly=True, compute='',
	# 	help="It indicates that the invoice has been paid and the journal entry of the invoice has been reconciled with one or several journal entries of payment.")
	state = fields.Selection([
	('draft', 'Draft'),
	('refund', 'Refund'),
	('proforma', 'Pro-forma'),
	('proforma2', 'Pro-forma'),
	('open', 'Posted'),
	('paid', 'Paid'),
	('paid1', 'Direct Paid'),
	('cancel', 'Cancelled'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft', visible="draft,open,paid1")

	@api.one
	@api.depends(
		'state', 'currency_id', 'invoice_line_ids.price_subtotal',
		'move_id.line_ids.amount_residual',
		'move_id.line_ids.currency_id')
	def _compute_residual(self):
		pass
		# residual = 0.0
		# residual_company_signed = 0.0
		# sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
		# for line in self.sudo().move_id.line_ids:
		#     if line.account_id.internal_type in ('receivable', 'payable'):
		#         residual_company_signed += line.amount_residual
		#         if line.currency_id == self.currency_id:
		#             residual += line.amount_residual_currency if line.currency_id else line.amount_residual
		#         else:
		#             from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
		#             residual += from_currency.compute(line.amount_residual, self.currency_id)
		# self.residual_company_signed = abs(residual_company_signed) * sign
		# self.residual_signed = abs(residual) * sign
		# self.residual = abs(residual)
		# digits_rounding_precision = self.currency_id.rounding
		# if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
		#     self.reconciled = True
		# else:
		#     self.reconciled = False


	@api.multi
	def action_invoice_open(self):
		to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
		if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft','refund']):
			raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
		to_open_invoices.action_date_assign()
		# if self.state != 'open':
		# if to_open_invoices.payment_term_id.name == 'Immediate Payment':
		# 	JournalEntries = self.env['account.move'].search([('partner_id','=',to_open_invoices.partner_id.id)])
		# 	amount = 0
		# 	for rec in JournalEntries:
		# 		for line in rec.line_ids:
		# 			if line.account_id.id == to_open_invoices.partner_id.property_account_receivable_id.id:
		# 				amount += line.debit - line.credit
		# 	amount += to_open_invoices.amount_total
		if to_open_invoices.partner_id.stop_invoice == True:
			credit1 = to_open_invoices.partner_id.credit + to_open_invoices.amount_total
			credit_limit1 = to_open_invoices.partner_id.credit_limit
		# stop = to_open_invoices.partner_id.stop_invoice
		# to_open_invoices._check_total(credit1,credit_limit1,stop)
			if credit1 > credit_limit1:
				return {
				'type': 'ir.actions.act_window',
				'name': 'Customer Receipts',
				'res_model': 'customer.payment.bcube',
				'view_type': 'form',
				'view_mode': 'form',
				'target' : 'new',
				'context': {'default_partner_id': to_open_invoices.partner_id.id,'default_receipts': True}
				}
		if not to_open_invoices.pdc_module:
			if to_open_invoices.payment_term_id.name == 'Cheque Before Delivery':
				to_open_invoices.state == 'draft'
				return {
				'type': 'ir.actions.act_window',
				'name': 'Cheque And Balance',
				'res_model': 'pdc_bcube.pdc_bcube',
				'view_type': 'form',
				'view_mode': 'form',
				'target' : 'new',
				'context': {'default_customer': to_open_invoices.partner_id.id, 'default_inv_ref': to_open_invoices.id}
				}
		if to_open_invoices.stock_id:
			print to_open_invoices.stock_id.id
			to_open_invoices.stock_id.print_do = True
			to_open_invoices.stock_id.state = 'ready'

		if to_open_invoices.journal_id.type != 'cash':
			to_open_invoices.action_move_create()
		res = super(sale_invoice_customized, self).action_invoice_open()

		return to_open_invoices.invoice_validate()


	def action_invoice_cancel(self):
		new_record = super(sale_invoice_customized, self).action_invoice_cancel()

		if self.stock_id:
			self.stock_id.state = 'cancel'

		return new_record

		# [('type','in',('out_invoice', 'out_refund'))]


	# @api.multi
	# @api.constrains()
	# def _check_total(self,credit,credit_limit,stop):
	# 	if stop == True:
	# 		if credit > credit_limit:
	# 			raise ValidationError('Amount is exceeding credit limit')

	@api.multi
	def compute_remaining_days(self):
		invoices = self.env['account.invoice'].search([('state','=',"open")])
		current_date = fields.date.today()
		current_date = str(current_date)
		for x in invoices:
			fmt = '%Y-%m-%d'
			d1 = datetime.strptime(current_date, fmt)
			d2 = datetime.strptime(str(x.date_invoice),fmt)
			dayss = (d1-d2).days
			payment_days = int(x.payment_term_id.line_ids.days)

			due_days = int(str((d1-d2).days))

			x.due_days = due_days - payment_days

	@api.multi
	def get_due(self):
		rec = self.env['account.invoice'].search([('type','=','out_invoice')])
		for x in rec:
			if x.due_days >= 1:
				x.write({'due_check' : True})
			else:
				x.write({'due_check' : False})




	# @api.onchange('payment_term_id','date_invoice')
	# def count_total(self):
	# 	if self.date_invoice and self.payment_term_id:
	# 		current_date = fields.date.today()
	# 		date_start_dt = fields.Datetime.from_string(current_date)
	# 		dt 	= date_start_dt + relativedelta(days=self.payment_term_id.line_ids.days)
	# 		self.remaining_payment_days = fields.Datetime.to_string(dt)
	# 		fmt = '%Y-%m-%d'
	# 		d1 = datetime.strptime(current_date, fmt)
	# 		d2 = datetime.strptime(self.remaining_payment_days, fmt)
	# 		self.due_days = str((d1-d2).days)


	@api.multi
	def to_refund(self):
		self.state = 'refund'

		stock_pick = self.env['stock.picking.type'].search([('warehouse_id','=',self.warehouse.id),('name','=',"Receipts")])
		print stock_pick.default_location_dest_id.name
		inventory = self.env['stock.picking']
		inventory_lines = self.env['stock.pack.operation'].search([])
		inventory_lines_move = self.env['stock.move'].search([])
		location = self.env['stock.picking.type'].search([('warehouse_id','=',self.warehouse.id)])

		create_inventory = inventory.create({
			'partner_id':self.partner_id.id,
			'location_id':9,
			'refund': True,
			'picking_type_id' : stock_pick.id,
			'location_dest_id' : stock_pick.default_location_dest_id.id,
			'account_inv_id':self.id,

		})

		self.stock_id = create_inventory.id
		# create_inventory.state = "confirmed"
		for x in self.invoice_line_ids:
			create_inventory_lines= inventory_lines_move.create({
				'product_id':x.product_id.id,
				'product_uom_qty':x.quantity,
				'product_uom': x.product_id.uom_id.id,
				'location_id':9,
				'location_dest_id': stock_pick.default_location_dest_id.id,
				'name':x.product_id.name,
				'picking_id': create_inventory.id,
				})

			create_inventory.action_assign()
			create_inventory.force_assign()




class sale_invoice_line_extension(models.Model):
	_inherit = "account.invoice.line"

	uom = fields.Char(string="UOM", readonly="1")
	carton = fields.Float(string="Quantity (CARTONS)")
	cartons = fields.Float(string="Cartons")
	last_sale = fields.Float(string="Last Sale")  
	promo_code 		= fields.Many2one('naseem.sales.promo',string="PROMO CODE",readonly=True)
	customer_price = fields.Float(string="Net Price")
	price = fields.Many2one('product.pricelist.item')
	discount_own 	= fields.Float(string="Discount %")
	price_subtotal = fields.Float(string ="Total",compute = "get_total_price",store = True)




	@api.one
	@api.depends('quantity','customer_price')
	def get_total_price(self):
		self.price_subtotal = self.quantity * self.customer_price
		# if self.product_id.pcs_per_carton > 0:
		# 	self.carton = self.product_uom_qty/self.product_id.pcs_per_carton

	@api.one
	@api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
		'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
		'invoice_id.date_invoice')
	def _compute_price(self):
		pass
		# currency = self.invoice_id and self.invoice_id.currency_id or None
		# price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
		# taxes = False
		# if self.invoice_line_tax_ids:
		#     taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
		# self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
		# if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
		#     price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
		# sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
		# self.price_subtotal_signed = price_subtotal_signed * sign


	@api.onchange('product_id')
	def _onchange_unit_price(self):
		self.uom = self.product_id.uom
		if self.invoice_id.type == "out_refund":
			rec = self.env['account.invoice'].search([('partner_id','=',self.invoice_id.partner_id.id),('state','not in',['draft','cancel']),('type','=',"out_invoice")])
			print rec
			if rec:
				print "rececceee ccecececececececececec"

				rec = rec.sorted(key=lambda r: r.date_invoice)
				rec = rec[-1]
				last_sale = 0
				for x in rec.invoice_line_ids:
					print x.product_id.name
					if self.product_id.id == x.product_id.id and x.customer_price != 0:
						print "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
						last_sale = x.customer_price
				print last_sale
				self.customer_price = last_sale

	@api.multi
	@api.constrains('quantity')
	def check_sale_qty(self):
		if self.invoice_id.type == "out_refund":
			rec = self.env['account.invoice'].search([('partner_id','=',self.invoice_id.partner_id.id),('state','not in',['draft','cancel']),('type','=',"out_invoice")])
			total_sale = 0
			for x in rec:
				for y in x.invoice_line_ids:
					if self.product_id.id == y.product_id.id:
						total_sale = total_sale + y.quantity

			if self.quantity > total_sale:
				raise ValidationError('Quantity is greater than purchase') 


	@api.onchange('quantity','product_id')
	def _onchange_cartons(self):
		if self.product_id.pcs_per_carton > 0:
			self.carton = self.quantity / self.product_id.pcs_per_carton

	@api.onchange('carton')
	def get_pieces(self):
		self.quantity = round(self.carton * self.product_id.pcs_per_carton)





