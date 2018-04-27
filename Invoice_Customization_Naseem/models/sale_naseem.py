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

class sale_order_customized(models.Model):
	_inherit = 'sale.order'

	due_days 				= fields.Integer(string="Due Days", compute="compute_remaining_days")
	due 					= fields.Char(string="Due")
	transporter 			= fields.Many2one('res.partner',string="Transporter")
	delivery_id 			= fields.Many2one('stock.picking',string="Delivery Id",readonly=True)
	remaining_payment_days  = fields.Datetime(string="Remaining Payment Days")
	direct_invoice_check 	= fields.Boolean(string="Direct Invoice", readonly="1")
	saleperson_check 	    = fields.Boolean(string="check", readonly="1")
	journal 				= fields.Many2one('account.journal', string="Journal")
	types = fields.Selection([('cash', 'Cash'),('credit', 'Credit')],string="Type")
	state2 = fields.Selection([
	('draft', 'Draft'),
	('validate', 'Validate'),
	('cancel', 'Cancelled'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
	due = fields.Char()

	instant_promo = fields.One2many('instant.promo.so','instant_promo_id')
	
	
	state = fields.Selection([
	('draft', 'Quotation'),
	('sent', 'Quotation Sent'),
	('sale', 'Sales Order'),
	('done', 'Locked'),
	('assigned', 'Collect Cargo'),
	('waiting_approve', 'Waiting For Approval'),
	('ready', 'Ready For Delivery'),
	('cancel', 'Cancelled'),
	('partial', 'Partial'),
	('complete', 'Complete'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	warehouse_id = fields.Many2one(
		'stock.warehouse', string='Warehouse',
		required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
		default=None)


	# @api.multi
	# def error(self):
	# 	print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
	# 	sale_deliveries = self.env['stock.picking'].search([('origin','=',self.name)])
	# 	if sale_deliveries:
	# 		sale_deliveries.action_assign()
			# for x in sale_deliveries.move_lines:
			# 	x.state = "draft"
	# 		sale_deliveries.state = "draft"
	# 		for x in sale_deliveries.pack_operation_product_ids:
	# 			x.unlink()

	# 		operations = self.env['stock.picking.type'].search([('warehouse_id','=',self.warehouse_id.id),('name','=',"Delivery")])
	# 		print operations.name
	# 		sale_deliveries.picking_type_id = 4
	# 		print "yyyyyyyyyyyyyyyyyyyyyyyy"

	# 		sale_deliveries.action_assign()
	# 		# sale_deliveries.force_assign()
	# 		# self.state = "draft"
			
	# 		# print self.picking_ids.id
	# 		# self.picking_ids = False 
	# 	else:
	# 		raise ValidationError('No Pending Delivery Exists for this Sale Order')


	@api.onchange('partner_id')
	def refresh_lines(self):
		for x in self.order_line:
			x.check_pricelist_lastSale_Promo()
			if x.price:
				x.get_price()

	@api.multi
	def make_delivery(self):
		sale_deliveries = self.env['stock.picking'].search([('origin','=',self.name),('backorder','=',True)])
		if sale_deliveries:
			sale_deliveries.backorder = False
		else:
			raise ValidationError('No Pending Delivery Exists for this Sale Order')

	@api.multi
	def complete_order(self):
		return {
		'type': 'ir.actions.act_window',
		'name': 'Add Products',
		'res_model': 'sale.approve',
		'view_type': 'form',
		'view_mode': 'form',
		'target' : 'new',
		}
		# if self.direct_invoice_check == True:
		# 	self.state2 = "complete"
		# else:
		# 	self.state = "complete"
		# back_order = self.env['stock.picking'].search([('origin','=',self.name),('state','not in',('done','cancel'))])
		# if back_order:
		# 	print "Found"
		# 	print "xxxxXXXxxxXXXXxxxxxxxxxxx"
		# 	back_order.state = "cancel"


	@api.multi
	def generate_wizard(self):
		return {
		'type': 'ir.actions.act_window',
		'name': 'Add Products',
		'res_model': 'wizard.class',
		'view_type': 'form',
		'view_mode': 'form',
		'target' : 'new',
		}

	# incoterm = fields.Many2one('stock.incoterms')
###################################################

	@api.onchange('instant_promo')
	def get_per_carton(self):

		for x in self.instant_promo:
			if x.qty > 0:
				if x.product_id.pcs_per_carton > 0:
					x.qty_per_crt = x.qty / x.product_id.pcs_per_carton

	@api.one
	def compute_remaining_days(self):
		current_date = fields.Datetime.now()
		if self.date_order and self.payment_term_id and self.remaining_payment_days:
			fmt = '%Y-%m-%d %H:%M:%S'
			d1 = datetime.strptime(current_date, fmt)
			d2 = datetime.strptime(self.remaining_payment_days, fmt)
			self.due_days = str((d1-d2).days)


	@api.onchange('payment_term_id','date_order')
	def count_total(self):
		if self.date_order and self.payment_term_id:
			date_start_dt = fields.Datetime.from_string(self.date_order)
			dt 	= date_start_dt + relativedelta(days=self.payment_term_id.line_ids.days)
			self.remaining_payment_days = fields.Datetime.to_string(dt)
			fmt = '%Y-%m-%d %H:%M:%S'
			d1 = datetime.strptime(self.date_order, fmt)
			d2 = datetime.strptime(self.remaining_payment_days, fmt)
			self.due_days = str((d1-d2).days)


	@api.onchange('partner_id')
	def select_journal(self):
		if not self.journal:
			cash_journal = self.env['account.journal'].search([('type','=','cash')])
			if cash_journal:
				self.journal = cash_journal.id
		journal_env_cash = self.env['account.journal'].search([('type','=',"cash")])
		journal_env_sale = self.env['account.journal'].search([('type','=',"sale")])

		if self.partner_id:	
			self.transporter = self.partner_id.transporter
			
			self.incoterm = self.partner_id.incoterm
			self.payment_term_id = self.partner_id.payment_term.id
			self.currency_id = self.partner_id.currency
			if self.partner_id.user_id:
				self.user_id = self.partner_id.user_id.id
				self.saleperson_check = True
			else:
				users = self.env['res.users'].search([('id','=',self._uid)])
				self.user_id = users.id
				self.saleperson_check = False
			if self.direct_invoice_check == False:
				sale_journal = self.env['account.journal'].search([('type','=','sale')])
				self.journal = sale_journal.id


	@api.one
	@api.depends('partner_id')
	def get_payment_terms(self):
		print "xxxxxxxxxxxxxxxxxxxxxx"
		


	@api.onchange('types')
	def _cash_types(self):
		if self.types:
			if self.types == 'cash':
				cash_journal = self.env['account.journal'].search([('type','=','cash')])
				# check = self.env['hr.employee'].search([('user_id.id','=',self.user_id.id)])
				if cash_journal:
					self.journal = cash_journal.id
			else:
				sale_journal = self.env['account.journal'].search([('type','=','sale')])
				self.journal = sale_journal.id



	@api.multi
	def validate_direct_invoice(self):
		self.state2 = 'validate'

#####################################
#  Create Customer Invoice  
#####################################

		sale_order = self.env['sale.order'].search([('partner_id','=',self.partner_id.id),(('state','=',"sale"))])
		total = 0 
		for x in sale_order:
			total = total + x.amount_total

		if self.types == 'cash':
			cash_enteries = self.env['account.bank.statement'].search([('state','=','open')])
			if cash_enteries:
				inv = []
				for invo in self.order_line:
					inv.append({
						'date':self.date_order,
						'name':"payment",
						'partner_id':self.partner_id.id,
						'ref':self.name,
						'amount':self.amount_total,
						'line_ids':cash_enteries.id,
						})
				
				cash_enteries.line_ids = inv
				inv=[]

			# else:
			# 	raise ValidationError('Open Concerned Cash Book First')

			self.action_confirm()

			pickings = self.env['stock.picking'].search([('origin','=',self.name)])
			pickings.action_assign()
			if not pickings.pack_operation_product_ids:
				raise ValidationError('Stock not available') 
			pickings.approve()

			invoices = self.env['account.invoice'].search([('source','=',self.name)])
			invoices.action_invoice_open()
			pickings.do_new_transfer()
			invoices.residual = 0
			invoices.residual_signed = 0
			invoices.write({'state':"paid"})

		if self.types == "credit":
			self.action_confirm()

			pickings = self.env['stock.picking'].search([('origin','=',self.name)])
			pickings.action_assign()
			if not pickings.pack_operation_product_ids:
				raise ValidationError('Stock not available')
			pickings.approve()

			invoices = self.env['account.invoice'].search([('source','=',self.name)])
			invoices.action_invoice_open()
			pickings.do_new_transfer()
	

	@api.model
	def create(self, vals):	
		new_record = super(sale_order_customized, self).create(vals)
		self.delete_zero_products()
		return new_record



	@api.multi
	def write(self, vals):


		before_warehouse = self.warehouse_id.id
		res =super(sale_order_customized, self).write(vals)
		after_warehouse = self.warehouse_id.id

		if before_warehouse != after_warehouse and self.state != "draft":
			sale_deliveries = self.env['stock.picking'].search([('origin','=',self.name)])

			if len(sale_deliveries) == 1:
				sale_deliveries.unreserve()
				operations = self.env['stock.picking.type'].search([('warehouse_id','=',self.warehouse_id.id),('name','=',"Delivery Orders")])
				print operations.name
				sale_deliveries.picking_type_id = operations.id
				for x in sale_deliveries.move_lines:
					x.location_id = operations.default_location_src_id
				for x in sale_deliveries.pack_operation_product_ids:
					x.unlink()
				sale_deliveries.action_assign()




		self.delete_zero_products()
		return res
		
	def delete_zero_products(self):
		for lines in self.instant_promo:
			if lines.qty == 0:
				lines.unlink()

	@api.onchange('partner_id')
	def get_due_ammount(self):
		all_records = self.env['account.invoice'].search([('state','=',"open")])
		total_30  = 0
		total_60  = 0
		total_90  = 0
		total_120 = 0
		if self.partner_id:
			for x in all_records:
				if x.partner_id == self.partner_id:
					if x.due_days <=30:
						total_30 = total_30 + x.amount_total
					elif x.due_days <=60:
						total_60 = total_60 + x.amount_total
					elif x.due_days <=90:
						total_90 = total_90 + x.amount_total	
					else:
						total_120 = total_120 + x.amount_total	
			self.due = str(total_30) + "  (30 Days)       " + str(total_60) + "  (60 Days)       " +  str(total_90) + "  (90 Days)      " + str(total_120) + "  (120 Days)   " 

	@api.multi
	def action_confirm(self):
		for lines in self.instant_promo:
			self.order_line.create({
				'product_id': lines.product_id.id,
				'product_uom_qty':lines.qty,
				'product_uom': 1,
				'uom': lines.product_id.uom,
				'price_unit': 0,
				'carton': lines.qty_per_crt,
				'name': lines.product_id.name,
				'order_id':self.id
				})
		return  super(sale_order_customized,self).action_confirm()

	@api.constrains('order_line')
	def check_product_repeatetion(self):
		items= []
		flag = 0
		if self.product_id:
			for x in self.order_line:
				items.append(x.product_id.id)
		counter=collections.Counter(items)
		for x in counter.values():
			if x > 1:
				flag = 1
		if flag == 1:
			raise ValidationError('Same Product exists multiple times in Sale Order')

	@api.onchange('order_line','client_order_ref')
	def on_change_instant_promo(self):
		items= []
		flag = 0
		if self.product_id:
			for x in self.order_line:
				items.append(x.product_id.id)
		counter=collections.Counter(items)
		for x in counter.values():
			if x > 1:
				flag = 1
		if flag == 1:
			raise ValidationError('Same Product exists multiple times in Sale Order')
		else:
			instant_promo_lines = self.env['promo.instant'].search([('sales_promo_id5.scheme_from_dt','<=',self.date_order), ('sales_promo_id5.scheme_to_dt','>=',self.date_order), ('sales_promo_id5.stages','=',"validate")])
			sale_order_lines = self.env['sale.order.line'].search([])
			for x in self.order_line:
				for y in instant_promo_lines:
					if x.product_id.id == y.product.id and x.order_id.partner_id in y.sales_promo_id5.customer:
						invoice_lines = self.env['account.invoice.line'].search([('invoice_id.date','>=',y.sales_promo_id5.scheme_from_dt), ('invoice_id.date','<=',y.sales_promo_id5.scheme_to_dt),('product_id.id','=',y.product.id),('invoice_id.partner_id.id','=',self.partner_id.id),('invoice_id.state','!=',"draft")])
						current_quantity = 0
						for qt in self.order_line:
							if qt.product_id.id == y.product.id and qt.price_unit != 0:
								current_quantity = current_quantity + qt.product_uom_qty
						invoice_total = (self.quantity(invoice_lines)[0] - self.quantity(invoice_lines)[2]) + current_quantity
						invoice_total_promo =  self.quantity(invoice_lines)[1] - self.quantity(invoice_lines)[3]
						reward_quantity = (int(invoice_total/y.qty) * y.qty_reward) - invoice_total_promo
						ids = []
						for a in self.instant_promo:
							ids.append(a.product_id.id)
						if x.product_id.id not in ids and reward_quantity > 0:
							self.instant_promo |= self.instant_promo.new({'product_id':x.product_id.id,'qty': reward_quantity,'instant_promo_id': self.id,'manual':True})
						elif x.product_id.id in ids:
							for c in self.instant_promo:
								if c.product_id.id == x.product_id.id:
									if c.manual == True:
										c.qty = reward_quantity

			product_lst = []
			for y in self.order_line:
				product_lst.append(y.product_id.id)
			for lines in self.instant_promo:
				if lines.product_id.id not in product_lst:
					if lines.manual == True:
						lines.qty = 0


	def _prepare_instant_promo(self, product_id, qty, id):
		data = {
		'product_id':product_id,
		'qty': qty,
		'instant_promo_id': id,

		}
		return data

	
	def quantity(self,invoice):
		total_quantity = [0,0,0,0]
		for z in invoice:
			if z.invoice_id.type == "out_invoice":
				if z.price_unit != 0:
					total_quantity[0] = total_quantity[0] + z.quantity
				else:
					total_quantity[1] = total_quantity[1] + z.quantity
			elif z.invoice_id.type == "out_refund":
				if z.price_unit != 0:
					total_quantity[2] = total_quantity[2] + z.quantity
				else:
					total_quantity[3] = total_quantity[3] + z.quantity
		return total_quantity



################################################################################
#**************************************##**************************************#
#---------------------Sale Order Line -----------------------------------------#
#**************************************##**************************************#
################################################################################
class sale_order_line_extension(models.Model):
	_inherit = "sale.order.line"

	uom 			= fields.Char(string="UOM")
	carton 			= fields.Float(string="Quantity (CARTONS)")
	last_sale 		= fields.Float(string="Last Sale")  
	in_hand 		= fields.Float(string="In Hand")  
	promo_code 		= fields.Many2one('naseem.sales.promo')
	customer_price 	= fields.Float(string="Net Price",compute = "get_net_price",store = True)
	discount_own 	= fields.Float(string="Discount %")
	pricelist_ext 	= fields.Many2one('product.pricelist', string = "Pricelist")
	price 			= fields.Many2one('product.pricelist.item')
	check_boolean 	= fields.Boolean()
	set_list_price 	= fields.Boolean()
	price_subtotal = fields.Monetary(compute='get_total_price', string='Subtotal', readonly=True, store=True)
	# price_check 	= fields.Boolean()
	check_promo 	= fields.Boolean(string="Promo ?", default=False)
	trial_price_unit 	= fields.Float(string="local Price")


	@api.onchange('product_uom_qty', 'product_uom', 'route_id')
	def _onchange_product_id_check_availability(self):
		# pass
		if not self.product_id or not self.product_uom_qty or not self.product_uom:
			self.product_packaging = False
			return {}
		if self.product_id.type == 'product':
			precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
			product = self.product_id.with_context(warehouse=self.order_id.warehouse_id.id)
			product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
			if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
				is_available = self._check_routing()
				# if not is_available:
				# 	message =  _('You plan to sell %s %s but you only have %s %s available in %s warehouse.') % \
				# 			(self.product_uom_qty, self.product_uom.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
				# 	# We check if some products are available in other warehouses.
				# 	if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
				# 		message += _('\nThere are %s %s available accross all warehouses.') % \
				# 				(self.product_id.virtual_available, product.uom_id.name)

				# 	warning_mess = {
				# 		'title': _('Not enough inventory!'),
				# 		'message' : message
				# 	}
				# 	return {'warning': warning_mess}
		return {}
	
	

	# @api.onchange('product_id','product_uom_qty','customer_price','pricelist_ext')
	# def _onchange_product_line(self):
	# 	if self.product_id and self.pricelist_ext:
	# 		for item in self.pricelist_ext.item_ids:
	# 			if item.product_id.id == self.product_id.id:
	# 				if item.compute_price == 'fixed':
	# 					if item.fixed_price != 0.0:
	# 						self.price_unit = item.fixed_price
	# 				elif item.compute_price == 'formula':
	# 					if item.price_discount != 0.0:
	# 						self.price_unit = self.product_id.with_context(pricelist=item.base_pricelist_id.id).price
	# 						self.discount = item.price_discount

	# 				else:
	# 					raise Warning('Pls select compute price to fix or formula in the pricelist.')
	# 	return True


	@api.onchange('price')
	def get_price(self):
		self.price_unit = self.price.fixed_price

	@api.onchange('product_id')
	def check_pricelist_lastSale_Promo(self):
########################################
#       checking Pricelist
########################################
		if self.product_id:
			print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
			self.promo_code = False
			# self.product_uom_qty = 0
			# self.carton =0
			self.uom = self.product_id.uom
			self.name = self.product_id.name
			self.product_uom = 1
			self.set_list_price = False
			self.check_boolean = False
			self.in_hand = self.product_id.qty_available
			promolist = self.env['promo.customer'].search([('customer','=',self.order_id.partner_id.id),('stages','=',"confirm"),\
				('start_date','<=',self.order_id.date_order),('end_date','>=',self.order_id.date_order)])
			
			for x in promolist:
				if x.promotion.applicable_on == "product": 
					if x.promotion.scheme_application == "list_price" and x.promotion.prod_name == self.product_id:
						self.set_list_price = True
						list_price_rec = self.env['product.pricelist.item'].search([('pricelist_id.name','=',"List Price"),('product_id','=',self.product_id.id)])
						self.price = list_price_rec.id
						self.check_boolean = True
						self.promo_code = x.promotion.id


					else:
						self.set_list_price = False
				elif x.promotion.applicable_on == "category":
					if x.promotion.scheme_application == "list_price" and x.promotion.prod_cat == self.product_id.categ_id:
						self.set_list_price = True
						list_price_rec = self.env['product.pricelist.item'].search([('pricelist_id.name','=',"List Price"),('product_id','=',self.product_id.id)])
						self.price = list_price_rec.id
						self.check_boolean = True
						self.promo_code = x.promotion.id
					else:
						self.set_list_price = False

			if self.set_list_price == False:
				# self.price_unit = self.product_id.list_price_own
				pricelist = self.env['product.pricelist'].search([('id','=',self.order_id.partner_id.linked_pricelist.id)])
				pricelist_lines = self.env['product.pricelist.item'].search([('pricelist_id','=',pricelist.id),('product_id','=',self.product_id.id)])
				if not pricelist_lines:
					self.check_boolean = False
					self.price_unit = 0
					self.discount_own = 0
					list_price_rec = self.env['product.pricelist.item'].search([('pricelist_id.name','=',"List Price"),('product_id','=',self.product_id.id)])

					self.price = list_price_rec.id



				else:		
					for x in pricelist_lines:
						self.price = False
						if x.product_id.id == self.product_id.id or x.categ_id.id == self.product_id.categ_id.id:
							self.pricelist_ext = self.order_id.partner_id.linked_pricelist.id
							self.check_boolean = True
							if x.compute_price == "formula":
								print x.price_discount
								list_price_rec = self.env['product.pricelist.item'].search([('pricelist_id.name','=',"List Price"),('product_id','=',self.product_id.id)])
								self.price = list_price_rec.id
								self.price_unit = self.product_id.list_price_own
								self.discount_own = x.price_discount
								break
							if x.compute_price == "fixed":
								self.price_unit = x.fixed_price
								self.discount_own = 0
								break

			all_records = self.env['account.invoice'].search([('type','=',"out_invoice"),('partner_id','=',self.order_id.partner_id.id)])
			all_records = all_records.sorted(key=lambda r: r.date_invoice)
			for x in all_records:
				# if self.order_id.partner_id == x.partner_id:	
				for y in x.invoice_line_ids:
					if self.product_id == y.product_id:
						self.last_sale = y.customer_price



	@api.one
	@api.depends('price_unit','discount_own')
	def get_net_price(self):
		# if self.price.fixed_price != self.price_unit:
		# 	self.price = False
		self.customer_price = self.price_unit * (100-self.discount_own)/100

	@api.one
	@api.depends('product_uom_qty','customer_price')
	def get_total_price(self):
		self.price_subtotal = self.product_uom_qty * self.customer_price
		if self.product_id.pcs_per_carton > 0:
			self.carton = self.product_uom_qty/self.product_id.pcs_per_carton

	@api.onchange('carton')
	def get_pieces(self):
		if self.product_id.pcs_per_carton > 0:
			self.product_uom_qty = self.carton * self.product_id.pcs_per_carton
			self.product_uom_qty = round(self.product_uom_qty)



	@api.multi
	def _get_display_price(self, product):
		pass
		# if self.order_id.pricelist_id.discount_policy == 'without_discount':
		#     from_currency = self.order_id.company_id.currency_id
		#     return from_currency.compute(product.lst_price, self.order_id.pricelist_id.currency_id)
		# return product.with_context(pricelist=self.order_id.pricelist_id.id).price

	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):
		pass
		# if not self.product_id:
		#     return {'domain': {'product_uom': []}}

		# vals = {}
		# domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
		# if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
		#     vals['product_uom'] = self.product_id.uom_id
		#     vals['product_uom_qty'] = 1.0

		# product = self.product_id.with_context(
		#     lang=self.order_id.partner_id.lang,
		#     partner=self.order_id.partner_id.id,
		#     quantity=vals.get('product_uom_qty') or self.product_uom_qty,
		#     date=self.order_id.date_order,
		#     pricelist=self.order_id.pricelist_id.id,
		#     uom=self.product_uom.id
		# )

		# name = product.name_get()[0][1]
		# if product.description_sale:
		#     name += '\n' + product.description_sale
		# vals['name'] = name

		# self._compute_tax_id()

		# if self.order_id.pricelist_id and self.order_id.partner_id:
		#     vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
		# self.update(vals)

		# title = False
		# message = False
		# warning = {}
		# if product.sale_line_warn != 'no-message':
		#     title = _("Warning for %s") % product.name
		#     message = product.sale_line_warn_msg
		#     warning['title'] = title
		#     warning['message'] = message
		#     if product.sale_line_warn == 'block':
		#         self.product_id = False
		#     return {'warning': warning}
		# return {'domain': domain}

	@api.onchange('product_uom', 'product_uom_qty')
	def product_uom_change(self):
		pass
		# if not self.product_uom:
		#     self.price_unit = 0.0
		#     return
		# if self.order_id.pricelist_id and self.order_id.partner_id:
		#     product = self.product_id.with_context(
		#         lang=self.order_id.partner_id.lang,
		#         partner=self.order_id.partner_id.id,
		#         quantity=self.product_uom_qty,
		#         date_order=self.order_id.date_order,
		#         pricelist=self.order_id.pricelist_id.id,
		#         uom=self.product_uom.id,
		#         fiscal_position=self.env.context.get('fiscal_position')
			# )
		#     self.price_unit = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)


	@api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
	def _compute_amount(self):
		pass
		"""
		Compute the amounts of the SO line.
		"""
		# for line in self:
		#     price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
		#     taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
		#     line.update({
		#         'price_tax': taxes['total_included'] - taxes['total_excluded'],
		#         'price_total': taxes['total_included'],
		#         'price_subtotal': taxes['total_excluded'],
		#     })







class sale_order_line_extension(models.Model):
	_name = "sale.approve"

	@api.multi
	def approve_backorder(self):
		active_class = self.env['sale.order'].browse(self._context.get('active_id'))
		if active_class:
			if active_class.direct_invoice_check == True:
				active_class.state2 = "complete"
			else:
				active_class.state = "complete"
			back_order = self.env['stock.picking'].search([('origin','=',active_class.name),('state','not in',('done','cancel'))])
			if back_order:
				
				back_order.state = "cancel"


	