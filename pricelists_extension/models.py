# -*- coding: utf-8 -*-
import re

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp import _
from openerp.exceptions import Warning
from odoo.exceptions import UserError


class pricelist_product_configuration(models.Model):
	_name = 'pricelist.configuration'
	_rec_name = 'category'



	@api.onchange('type_pricelist')
	def check_list_type(self):
		if self.type_pricelist == "normal":
			self.customer = False
			self.based_on = False

	@api.one
	@api.constrains('category','type_pricelist','customer','category_discount')
	def _check_date(self):


		if self.type_pricelist == "normal":
			all_cat_ids = self.env['pricelist.configuration'].search([('id','!=',self.id),('stages','!=',"inactivate"),('category','=',self.category.id),('type_pricelist','=','normal')])
			if all_cat_ids:
				raise ValidationError('Category already exists')

		if self.type_pricelist == "customer":
			all_cat_ids = self.env['pricelist.configuration'].search([('id','!=',self.id),('stages','!=',"inactivate"),('category','=',self.category.id),('customer','=',self.customer.id),('type_pricelist','=','customer')])
			if all_cat_ids:
				raise ValidationError('Category already exists')

		if self.category_discount >= 100 or self.category_discount < 0:
			raise ValidationError('Discount must be below 100 percent')





	category 			= fields.Many2one('product.category' , required = True)
	category_discount 	= fields.Float('Discount')
	get_products_id 	= fields.One2many('get.products','pricelist_configuration')
	get_products_id1 	= fields.One2many('get.products','pricelist_configuration')
	get_products_id2 	= fields.One2many('get.products','pricelist_configuration')
	customer 			= fields.Many2one('res.partner',domain="[('customer','!=', False)]")
	check_list 			= fields.Char(string="Check Lists")
	type_pricelist     	= fields.Selection([
		('normal', 'Normal'),
		('customer', 'Customer Based'),
		],default='normal')
	based_on     = fields.Selection([
		('discount_cat', 'Discount Category Wise'),
		('discount_prod', 'Discount Product Wise'),
		('fixed_price', 'Fixed Price'),
		],string = "Based On")
	stages     = fields.Selection([
		('draft', 'Draft'),
		('validate', 'Validate'),
		('inactivate', 'Deactivate'),
		],string = "Stages", default = 'draft')
	unique_record_name = fields.Char()




	@api.multi
	def validate(self):
		self.stages = "validate"

	@api.multi
	def generate_products(self):
		all_products = self.env['product.product'].search([])
		products_tree_view = self.env['get.products'].search([])
		emp_list = []
		for x in self.get_products_id:
			emp_list.append(x.product_id.id)
		all_prod = []
		for x in all_products:
			if x.categ_id.id == self.category.id:
				all_prod.append(x.id)
			if x.categ_id.id == self.category.id and x.id not in emp_list:
				generate_products_tree = products_tree_view.create({
					'product_id': x.id,
					'pricelist_configuration':self.id,
					})


	@api.multi
	def inactive_pricelist(self):
		self.stages="inactivate"
		if self.type_pricelist == 'normal':
			for x in self.get_products_id:
				# for rec in x.prod_price_list_id:
				ProductPricelist = self.env['product.pricelist.item'].search([('config_id','=',x.id)])
				for y in ProductPricelist:
					y.unlink()
		if self.type_pricelist == 'customer' and self.based_on == 'discount_prod':
			for x in self.get_products_id1:
				ProductPricelist = self.env['product.pricelist.item'].search([('config_id','=',x.id)])
				for y in ProductPricelist:
					y.unlink()
		if self.type_pricelist == 'customer' and self.based_on == 'fixed_price':
			for x in self.get_products_id2:
				ProductPricelist = self.env['product.pricelist.item'].search([('config_id','=',x.id)])
				for y in ProductPricelist:
					y.unlink()


		if self.type_pricelist == 'customer' and self.based_on == 'discount_cat':
			uni_id = str(self.id) + "dc"
			ProductPricelist = self.env['product.pricelist.item'].search([('config_id','=',uni_id)])
		
			ProductPricelist.unlink()


		


	@api.multi
	def update_pricelist_rule(self,product,price,pricelist_name,line_id,applied,price_compute,base,base_pricelist_id,price_discount,categ_id):
		pricelist = self.env['product.pricelist'].search([('name','=', pricelist_name)])

		pricelists_rules = self.env['product.pricelist.item'].search([('config_id','=',line_id),('pricelist_id','=',pricelist.id)])


		if not pricelists_rules:
			create_new_rule_list = pricelists_rules.create({
						'applied_on':applied,
						'compute_price':price_compute,
						'product_id':product,
						'fixed_price':price,
						'pricelist_id':pricelist.id,
						'config_id':line_id,
						'base':base,
						'base_pricelist_id':base_pricelist_id,
						'price_discount': price_discount,
						'categ_id':categ_id,
						'name':str(pricelists_rules.pricelist_id.name) + " - " + str(pricelists_rules.fixed_price)
						})

	
		else:
			if self.based_on == "fixed_price" or self.type_pricelist == "normal":
				pricelists_rules.fixed_price = price
				pricelists_rules.name = str(pricelists_rules.pricelist_id.name) + " - " + str(pricelists_rules.fixed_price)
			else:
				pricelists_rules.price_discount = price_discount

	@api.multi
	def update_pricelist(self):


		self._check_date()


		self.stages="validate"


		if self.type_pricelist == "normal":
			for items in self.get_products_id:
				self.update_pricelist_rule(items.product_id.id,items.list_price,"List Price",items.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)
				self.update_pricelist_rule(items.product_id.id,items.price_level1,"Level 1",items.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)
				self.update_pricelist_rule(items.product_id.id,items.price_level2,"Level 2",items.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)
				self.update_pricelist_rule(items.product_id.id,items.price_level3,"Level 3",items.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)

				items.product_id.list_price_own = items.list_price
				items.product_id.level_1 = items.price_level1
				items.product_id.level_2 = items.price_level2
				items.product_id.level_3 = items.price_level3

		else:
			if not self.customer.linked_pricelist:
				create_new_pricelist = self.env['product.pricelist'].create({
					'name': self.customer.name,
					})
				for records in create_new_pricelist.item_ids:
					records.unlink()
				self.customer.linked_pricelist = create_new_pricelist.id

			if self.based_on == "fixed_price":
				for y in self.get_products_id2:
					fixed_price = self.update_pricelist_rule(y.product_id.id,y.fixed_price,self.customer.name,y.id,"0_product_variant","fixed",base=None,base_pricelist_id=None,price_discount=None,categ_id=None)

			if self.based_on == "discount_cat":
				uni_id = str(self.id) + "dc"
				discount_cat = self.update_pricelist_rule(None,None,self.customer.name,uni_id,"2_product_category","formula","pricelist",2,self.category_discount,self.category.id)
			if self.based_on == "discount_prod":
			     for prod in self.get_products_id1:
					discount_prod = self.update_pricelist_rule(prod.product_id.id,None,self.customer.name,prod.id,"0_product_variant","formula","pricelist",2,prod.discount_percentage,None)



class PricelistLineExtension(models.Model):
	_inherit = 'product.pricelist.item'



	name = fields.Char(compute=None)
	config_id = fields.Char()
	categ_id = fields.Many2one(
        'product.category', 'Product Category',required = False, ondelete='cascade',
        help="Specify a product category if this rule only applies to products belonging to this category or its children categories. Keep empty otherwise.")
	base = fields.Selection([
		('list_price', 'Public Price'),
		('standard_price', 'Cost'),
		('pricelist', 'Other Pricelist')], "Based on",
		default='list_price',required = False,
		help='Base price for computation.\n'
		'Public Price: The base price will be the Sale/public Price.\n'
		'Cost Price : The base price will be the cost price.\n'
		'Other Pricelist : Computation of the base price based on another Pricelist.')




	@api.model
	def create(self, vals):
		new_record = super(PricelistLineExtension, self).create(vals)
		new_record.name = str(new_record.pricelist_id.name) + " - " + str(new_record.fixed_price)

		return new_record





class link_pricelist(models.Model):
	_inherit = 'res.partner'

	linked_pricelist = fields.Many2one('product.pricelist', string = "Linked Pricelist", readonly = True)
	





class get_products_category(models.Model):
	_name = 'get.products'

	product_id               = fields.Many2one('product.product',string = "Product", readonly = "True" , required = True)
	list_price               = fields.Float   (string = "List Price")
	price_level1             = fields.Float (string = "Level 1")
	price_level2             = fields.Float (string = "Level 2")
	price_level3             = fields.Float (string = "Level 3")
	fixed_price              = fields.Float (string = "Fixed Price")
	discount_percentage      = fields.Float (string = "Discount Percentage")
	category                 = fields.Many2one ('product.category')
	pricelist_configuration  = fields.Many2one('pricelist.configuration')
	prod_price_list_id   = fields.Many2many('product.pricelist.item', ondelete='cascade', string="Pricelist id")



	@api.one
	@api.constrains('discount_percentage','list_price','price_level1','price_level2','price_level3','fixed_price')
	def check_discount(self):
		if self.discount_percentage >= 100 or self.discount_percentage < 0:
			raise ValidationError('Discount must be below 100 percent')
		if self.list_price < 0 or self.price_level1 < 0 or self.price_level2 < 0 or self.price_level3 < 0 or self.fixed_price < 0:
			raise ValidationError('Price must be in positive')
	@api.model
	def create(self, vals):
		res = super(get_products_category, self).create(vals)
		PricelistConfig = self.env['pricelist.configuration'].search([('id','=',res.pricelist_configuration.id)])
		PricelistConfig.update_pricelist()
		return res


	@api.multi
	def write(self, vals):
		res = super(get_products_category, self).write(vals)
		PricelistConfig = self.env['pricelist.configuration'].search([('id','=',self.pricelist_configuration.id)])
		PricelistConfig.update_pricelist()
		return res


	@api.multi
	def unlink(self):
		ProductPricelist = self.env['product.pricelist.item'].search([('config_id','=',self.id)])
		ProductPricelist.unlink()
		res = super(get_products_category,self).unlink()
		return res

class BankExtend(models.Model):
	_inherit = 'account.journal'

	bank_address = fields.Char(string="Bank Address")

class HrExtend(models.Model):
	_inherit = "hr.employee"


	cash_book = fields.Many2one('account.journal',string="Cash Book")