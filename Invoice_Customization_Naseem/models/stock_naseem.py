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


class stock_picking_own(models.Model):
	_inherit 	= 'stock.picking'

	partner_id = fields.Many2one(string = "Partner", readonly = True)
	origin = fields.Char(string = "Source", readonly = True)
	backorder 		= fields.Boolean(string="Back Order", invisible=True)
	bilty_no  		= fields.Char(string="Billty No.")
	del_records     = fields.Many2one('sale.order')
	cash_book_id    = fields.Many2one('account.bank.statement',string="Cash Book")
	account_inv_id  = fields.Many2one('account.invoice',string="Invoice Id")
	print_do 		= fields.Boolean(string="Print DC")
	direct_inv		= fields.Boolean(string="Direct Invoice")
	refund			= fields.Boolean(string="Refund")
	inv_type		= fields.Char(string="Invoice Type")
	# bilty_recieved  = fields.Float(string="Billty Expense Received")
	packing_expense = fields.Float(string="Packing Expenses Paid")
	bilty_paid 		= fields.Float(string="Bilty Amount Paid")
	# bilty_amt_paid  = fields.Float(string="Bilty Amount Paid")
	bilty_amt_recev = fields.Float(string="Bilty Amount Recev")
	bilty_attach    = fields.Binary(string="Bilty Attachment")
	# pack_exp_paid   = fields.Float(string="Packing Expenses Paid")
	pack_exp_recev  = fields.Float(string="Packing Expenses Received")
	received_by 	= fields.Char(string="Received by")
	transporter 	= fields.Many2one('res.partner',string="Transporter")
	receipt 	= fields.Boolean(string="Receipt")
	move_type = fields.Selection([
        ('direct', 'As soon as possible'), ('one', 'When all products are ready')], 'Shipping Policy',
        default='direct', required=True,readonly = True,
        help="It specifies goods to be deliver partially or all at once")

	picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',required=True,readonly = True)


	reference_no 	= fields.Char(string="Reference")
	carton_no		= fields.Char(string="No. of Carton")
	bundle_no		= fields.Char(string="No. of Bundles")
	delivered_by	= fields.Char(string="Delivered By")
	warehouse 		= fields.Many2one('account.bank.statement',string="Cash Account")

	state = fields.Selection([
		('draft', 'Draft'),
		('cancel', 'Cancelled'),
		('confirmed', 'Waiting Availability'),
		('partially_available', 'Partially Available'),
		('assigned', 'Collect Cargo'),
		('waiting_approve', 'Waiting For Approval'),
		('ready', 'Ready For Delivery'),
		('done', 'Done'),
		('complete', 'Complete'),
		('close', 'Closed'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


	@api.one
	def compute_receipt(self):
		if self.picking_type_id.name == "Receipts":
			self.receipt = True

	@api.multi
	def unreserve(self):
		for x in self.move_lines:
			x.state = 'draft'

	@api.model
	def create(self, vals):
		new_record = super(stock_picking_own, self).create(vals)

		records = self.env['sale.order'].search([('name','=',new_record.origin)])
		if records.direct_invoice_check == False:
			new_record.transporter = records.transporter
		if new_record.picking_type_id.name == "Receipts":
			new_record.receipt = True		

		return new_record

	@api.multi
	def write(self, vals):

		res =super(stock_picking_own, self).write(vals)
		if self.picking_type_id.name == "Receipts":
			vals = {'receipt' : True
			}
		return res


	@api.multi
	def approve(self):
		qty = 0
		for x in self.pack_operation_product_ids:
			qty = qty + x.qty_done
		if qty == 0:
			for x in self.pack_operation_product_ids:
				x.qty_done = x.product_qty
				x.carton_done = x.carton_to

		if self.account_inv_id.type == "out_refund":

			for z in self.account_inv_id.invoice_line_ids:
				print z.quantity
				for y in self.pack_operation_product_ids:
					if z.product_id.id == y.product_id.id:
						z.quantity = y.qty_done
			self.account_inv_id.state = "draft"
			self.account_inv_id.action_invoice_open()
			self.do_transfer()
		else:
			
			self.state = 'waiting_approve'
			current_date = fields.date.today()



			sale_order = self.env['sale.order'].search([('name','=',self.origin)])
			invoice = self.env['account.invoice'].search([])
			invoice_lines = self.env['account.invoice.line'].search([])
			if sale_order:
				create_invoice = invoice.create({
					'journal_id': sale_order.journal.id,
					'partner_id':sale_order.partner_id.id,
					'transporter':sale_order.transporter.id,
					# 'remaining_payment_days':sale_order.remaining_payment_days,
					'due' : sale_order.due,
					'user_id' : sale_order.user_id.id,
					'payment_term_id' : sale_order.payment_term_id.id,
					# 'due_days' : sale_order.due_days,
					'date_invoice' : current_date,
					'incoterm' : sale_order.incoterm.id,
					'source' : sale_order.name,
					'stock_id' : self.id,
					'type': "out_invoice",
					'account_id':sale_order.partner_id.property_account_receivable_id.id
					})

				self.account_inv_id = create_invoice.id

				for x in sale_order.order_line:
					for y in self.pack_operation_product_ids:
						if x.product_id.id == y.product_id.id:
							if y.qty_done >0:
								y.lots_visible =True
								if x.product_id.property_account_income_id.id:
									account_id = x.product_id.property_account_income_id.id
								else:
									account_id = x.product_id.categ_id.property_account_income_categ_id.id	

								create_invoice_lines= invoice_lines.create({
									'product_id':x.product_id.id,
									'uom':x.uom,
									'quantity': y.qty_done,
									'carton': y.qty_done/x.product_id.pcs_per_carton,
									'last_sale': x.last_sale,
									'price': x.price.id,
									'price_unit': x.price_unit,
									'discount_own': x.discount_own,
									'customer_price': x.customer_price,
									'price_subtotal': x.price_subtotal,
									'promo_code': x.promo_code.id,
									'account_id': account_id,
									'name' : x.name,
									'invoice_id' : create_invoice.id,
									})
		# create_invoice.count_total()






	@api.multi
	def submitt_bilty(self):

		self.state = 'complete'

	@api.multi
	def post_enteries(self):

		if self.cash_book_id:
			for x in self.cash_book_id:
				for y in x.line_ids:
					if y.bilty_link.id == self.id:
						y.date = self.min_date
						y.name = self.reference_no
						y.ref= self.reference_no
						y.partner = self.partner_id.id
						y.amount = self.bilty_paid + self.packing_expense
		else:
			cash_enteries = self.env['account.bank.statement'].search([('journal_id.name','=',self.warehouse.name),('state','=','open')])
			if cash_enteries:
					inv = []
					inv.append({
						'date':self.min_date,
						'name':self.reference_no,
						'partner_id':self.partner_id.id,
						'ref':self.reference_no,
						'amount':self.bilty_paid + self.packing_expense,
						'bilty_link': self.id,
						'line_ids':cash_enteries.id,
						})

					self.cash_book_id = cash_enteries.id
					
					cash_enteries.line_ids = inv
					inv=[]
			else:
				raise ValidationError('Open Concerned Cash Book First')



	def do_new_transfer(self):
		new_record = super(stock_picking_own, self).do_new_transfer()
		if self.receipt == False:
			if self.account_inv_id.type != "out_refund":
				sale_order = self.env['sale.order'].search([('name','=',self.origin)])
				
			# self._invoice_creation_sale(sale_order ,self.pack_operation_product_ids)
				sale_order.state = "complete"
		self.creat_receipt_invoice()


		return new_record


	def creat_receipt_invoice(self):
		if self.receipt == True:
			# purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
			# purchase
			current_date = fields.date.today()
			purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])

			invoice = self.env['account.invoice'].search([])
			invoice_lines = self.env['account.invoice.line'].search([])
			journal = self.env['account.journal'].search([('code','=',"BILL")])
			total_done = 0
			for lines in self.pack_operation_product_ids:
				total_done = total_done + lines.qty_done

			if purchase_order and total_done > 0:
				create_invoice = invoice.create({
					'journal_id': journal.id,
					'partner_id':purchase_order.partner_id.id,
					# 'transporter':sale_order.transporter.id,
					# # 'remaining_payment_days':sale_order.remaining_payment_days,
					# 'due' : sale_order.due,
					# 'user_id' : sale_order.user_id.id,
					# 'payment_term_id' : sale_order.payment_term_id.id,
					# # 'due_days' : sale_order.due_days,
					'date_invoice' : current_date,
					'incoterm' : purchase_order.incoterm.id,
					'source' : purchase_order.name,
					'stock_id' : self.id,
					'type': "in_invoice",
					'account_id':purchase_order.partner_id.property_account_receivable_id.id
					})

				self.account_inv_id = create_invoice.id

				for x in purchase_order.order_line:
					for y in self.pack_operation_product_ids:
						if x.product_id.id == y.product_id.id:
							if y.qty_done >0:
								y.lots_visible =True
								if x.product_id.property_account_income_id.id:
									account_id = x.product_id.property_account_income_id.id
								else:
									account_id = x.product_id.categ_id.property_account_income_categ_id.id	

								create_invoice_lines= invoice_lines.create({
									'product_id':x.product_id.id,
									'quantity': y.qty_done,
									'price_unit': x.ecube_unit_price,
									# 'price_subtotal': x.ecube_subtotal,
									'customer_price': x.ecube_unit_price,
									'account_id': account_id,
									'name' : x.name,
									'invoice_id' : create_invoice.id,
									})


	
		


	def cron_action_assign(self):
		pickings = self.env['stock.picking'].search([('state','in',["confirmed","partially_available"])])
		for x in pickings:
			x.action_assign()

	def action_assign(self):
		new_record = super(stock_picking_own, self).action_assign()
		for y in self.pack_operation_product_ids:
			y.carton_to = y.product_qty / y.product_id.pcs_per_carton

		return new_record

	def force_assign(self):
		new_record = super(stock_picking_own, self).force_assign()

		for y in self.pack_operation_product_ids:
			y.carton_to = y.product_qty / y.product_id.pcs_per_carton

		return new_record


	# def _invoice_creation_sale(self, sale_order ,pack_operation_product_ids):
	# 	# sale_order = self.env['sale.order'].search([('name','=',self.origin)])
	# 	# purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
	# 	if not self.account_inv_id and self.refund == False:
	# 		qty = 0
	# 		for x in pack_operation_product_ids:
	# 			qty = qty + x.qty_done
	# 		if qty == 0:
	# 			for x in pack_operation_product_ids:
	# 				x.qty_done = x.product_qty
	# 				x.carton_done = x.carton_to
			
	# 		invoice = self.env['account.invoice'].search([])
	# 		invoice_lines = self.env['account.invoice.line'].search([])
	# 		if sale_order:
	# 			create_invoice = invoice.create({
	# 				'journal_id': sale_order.journal.id,
	# 				'partner_id':sale_order.partner_id.id,
	# 				'transporter':sale_order.transporter.id,
	# 				'remaining_payment_days':sale_order.remaining_payment_days,
	# 				'due' : sale_order.due,
	# 				'user_id' : sale_order.user_id.id,
	# 				'payment_term_id' : sale_order.payment_term_id.id,
	# 				'due_days' : sale_order.due_days,
	# 				'date_invoice' : sale_order.date_order,
	# 				'incoterm' : sale_order.incoterm.id,
	# 				'source' : sale_order.name,
	# 				'stock_id' : self.id,
	# 				})

	# 			self.account_inv_id = create_invoice.id

	# 			for x in sale_order.order_line:

	# 				for y in pack_operation_product_ids:

	# 					if x.product_id.id == y.product_id.id:
	# 						if x.product_id.property_account_income_id.id:
	# 							account_id = x.product_id.property_account_income_id.id
	# 						else:
	# 							account_id = x.product_id.categ_id.property_account_income_categ_id.id	
	# 						create_invoice_lines= invoice_lines.create({
	# 							'product_id':x.product_id.id,
	# 							'uom':x.uom,
	# 							'quantity': y.qty_done,
	# 							'carton': qty/x.product_id.pcs_per_carton,
	# 							'last_sale': x.last_sale,
	# 							'price': x.price.id,
	# 							'price_unit': x.price_unit,
	# 							'discount': x.discount,
	# 							'customer_price': x.customer_price,
	# 							'price_subtotal': x.price_subtotal,
	# 							'promo_code': x.promo_code.id,
	# 							'account_id': account_id,
	# 							'name' : x.name,
	# 							'invoice_id' : create_invoice.id,
	# 							})

	# 	if self.account_inv_id and self.refund == True:
	# 		for x in self.account_inv_id:
	# 			x.state = 'draft'
	# 			x.action_invoice_open()



	@api.multi
	def _create_backorder(self, backorder_moves=[]):
		""" Move all non-done lines into a new backorder picking. If the key 'do_only_split' is given in the context, then move all lines not in context.get('split', []) instead of all non-done lines.
		"""
		# TDE note: o2o conversion, todo multi

		backorders = self.env['stock.picking']
		for picking in self:
			backorder_moves = backorder_moves or picking.move_lines
			if self._context.get('do_only_split'):
				not_done_bo_moves = backorder_moves.filtered(lambda move: move.id not in self._context.get('split', []))
			else:
				not_done_bo_moves = backorder_moves.filtered(lambda move: move.state not in ('done', 'cancel'))
			if not not_done_bo_moves:
				continue
			backorder_picking = picking.copy({
				'name': '/',
				'move_lines': [],
				'pack_operation_ids': [],
				'backorder_id': picking.id,
				'backorder':True,
			})
			picking.message_post(body=_("Back order <em>%s</em> <b>created</b>.") % (backorder_picking.name))
			not_done_bo_moves.write({'picking_id': backorder_picking.id})
			if not picking.date_done:
				picking.write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
			backorder_picking.action_confirm()
			backorder_picking.action_assign()
			backorders |= backorder_picking



		# purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
		# sale_order = self.env['sale.order'].search([('name','=',self.origin)])
		# if purchase_order:
		# 	purchase_order.state = "partial"
		# if sale_order:
		# 	sale_order.state= "partial"

		return backorders




class stock_pack_extension(models.Model):
	_inherit 	= 'stock.pack.operation'

	carton_to 	= fields.Float(string="Carton To Do",readonly=True)
	carton_done = fields.Float(string="Carton Done")
	lots_visible = fields.Boolean(compute = "")

	@api.onchange('product_qty')
	def calculate_cartons_to(self):
		if self.product_qty:
			self.carton_to = int(self.product_qty / self.product_id.pcs_per_carton)

	@api.onchange('carton_to')
	def round_carton_to(self):
		if self.carton_to:
			self.carton_to = round(self.carton_to)
			self.product_qty = int(self.carton_to * self.product_id.pcs_per_carton)

	@api.onchange('carton_done')
	def calculate_cartons_done(self):
		if self.product_id.pcs_per_carton > 0:
			self.qty_done = self.carton_done * self.product_id.pcs_per_carton
			self.qty_done = round(self.qty_done)

	@api.onchange('qty_done')
	def calculate_qty_done(self):
		if self.product_id.pcs_per_carton > 0:
			self.carton_done =  self.qty_done/self.product_id.pcs_per_carton

class stock_immediate_transfer_naseem(models.TransientModel):
	_inherit 	= 'stock.immediate.transfer'

	def process(self):
		super(stock_immediate_transfer_naseem, self).process()
		stock_picking_id = self.env['stock.picking'].search([('name','=',self.pick_id.name)])
		sale_order = self.env['sale.order'].search([('name','=',stock_picking_id.origin)])
		# stock_picking_id._invoice_creation_sale(sale_order, stock_picking_id.pack_operation_product_ids)
		stock_picking_id.creat_receipt_invoice()


class stock_backorder_transfer_naseem(models.TransientModel):
	_inherit 	= 'stock.backorder.confirmation'

	def process(self):
		result = super(stock_backorder_transfer_naseem, self).process()

		stock_picking_id1 = self.env['stock.picking'].search([('name','=',self.pick_id.name)])
		if stock_picking_id1.receipt == False:
			sale_order = self.env['sale.order'].search([('name','=',stock_picking_id1.origin)])
		# stock_picking_id1._invoice_creation_sale(sale_order, stock_picking_id1.pack_operation_product_ids)
			sale_order.state = "partial"
		stock_picking_id1.creat_receipt_invoice()
		return result


class stock_warehouse_extension(models.Model):
	_inherit 	= 'stock.warehouse'

	address = fields.Char(string="Address")

class stock_user(models.Model):
	_inherit 	= 'res.users'

	@api.model
	def create(self, vals):
		new_record = super(stock_user, self).create(vals)
		new_record.partner_id.customer = False


		return new_record

class stock_loc_wise(models.Model):
	_inherit 	= 'stock.quant'

	carton = fields.Float(string="Cartons", compute="compute_cartons")

	@api.one
	def compute_cartons(self):
		if self.product_id.pcs_per_carton > 0:
			self.carton = self.qty / self.product_id.pcs_per_carton


