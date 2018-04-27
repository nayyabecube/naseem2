# -*- coding: utf-8 -*- 
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError

class CustomerPayment(models.Model): 
	_name = 'customer.payment.bcube' 
	_rec_name = 'number'

	number = fields.Char()
	amount = fields.Float(string="Paid Amount" )
	date = fields.Date(string="Date", required = True ,default=fields.Date.context_today) 
	e_amount = fields.Float(string="Advance Amount")
	t_amount = fields.Float(string="Total Amount")
	reference = fields.Char(string="Payment Ref")
	name = fields.Char(string="Memo")
	total = fields.Float('Total Amount', compute='invoice_total' ,store=True)
	t_total = fields.Float('Total Tax', compute='tax_total' ,store=True)
	period_id = fields.Many2one('account.period', string="Period")
	customer_tree  = fields.One2many( 'customer.payment.tree','customer_payment_link')
	journal_id  = fields.Many2one('account.journal',string="Payment Method" , required=True)
	tax_link = fields.One2many('account.invoice.tax','payment_link')
	partner_id = fields.Many2one('res.partner',string="Customer / Supplier" , required=True)
	journal_entry_id = fields.Many2one('account.move',string="Journal Entry ID")
	taxes = fields.Many2many('account.tax', string="Taxes")
	receipts = fields.Boolean()
	state = fields.Selection([('draft', 'Draft'),('post', 'Posted'),], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
	active_user = fields.Char(string="Active User")

	@api.model
	def create(self, vals):
		new_record = super(CustomerPayment, self).create(vals)
		if new_record.receipts == True:
			new_record.number = self.env['ir.sequence'].next_by_code('customer.payment.bcube')
		else:
			new_record.number = self.env['ir.sequence'].next_by_code('supplier.payment.bcube')

		return new_record


	# @api.onchange('partner_id')
	# def load_invoice(self):
	# 	self.active_user = self._uid
		
	# 	if self.partner_id:
	# 		if self.receipts == True:
	# 			invoices = self.env['account.invoice'].search([('state','=',"open"),('type','=',"out_invoice"),('partner_id.id','=',self.partner_id.id)])
	# 			invoices = invoices.sorted(key=lambda r:r.date_invoice)
	# 			extra_amount =  self.partner_id.debit - self.partner_id.credit
	# 			data = self.env['account.move'].search([('partner_id.id','=',self.partner_id.id)])
	# 			cre = 0
	# 			deb = 0
	# 			value = 0
	# 			for x in data:
	# 				for z in x.line_ids:
	# 					cre = cre + z.credit
	# 					deb = deb + z.debit
	# 					value = cre - deb
	# 			if value > 0:
	# 				self.e_amount = value
	# 			self.t_amount = self.amount + self.e_amount				
	# 		else:
	# 			invoices = self.env['account.invoice'].search([('state','=',"open"),('type','=',"in_invoice"),('partner_id.id','=',self.partner_id.id)])
	# 			invoices = invoices.sorted(key=lambda r:r.date_invoice)
	# 			extra_amount =  self.partner_id.credit - self.partner_id.debit

	# 		if extra_amount > 0:
	# 			self.e_amount = extra_amount
	# 		else:
	# 			self.e_amount = 0
							
			# customer_tree = []
			# delete = []
			# delete = delete.append(2)
			# self.customer_tree = delete

			# inv = []
			# for invo in invoices:
			# 	inv.append({
			# 		'invoice':invo.number,
			# 		'date':invo.date_invoice,
			# 		'due_amount':invo.amount_total, 
			# 		'reconciled_amount' :0.00,
			# 		'invoice_id':invo.id
			# 		})
			
			# self.customer_tree = inv
			# inv=[]								
							
	# @api.onchange('amount','e_amount')
	# def Amount(self):
	# 	self.t_amount=self.amount+self.e_amount
					
	# @api.onchange('t_amount','tax_link','partner_id')
	# def onchangeAmount(self):

	# 	t_amount = self.t_amount + self.t_total

		# if self.customer_tree:
		# 	for line in self.customer_tree:
		# 		if t_amount >= line.due_amount:
		# 			line.reconciled_amount = line.due_amount
		# 			t_amount = t_amount - line.due_amount
		# 			if (line.reconciled_amount-line.due_amount)==0:
		# 							line.reconcile=True
										
		# 		elif t_amount < line.due_amount and t_amount !=0:
		# 			line.reconciled_amount =t_amount
		# 			line.reconcile=False
		# 			t_amount = 0
								

		# 		else:
		# 			line.reconciled_amount = 0
		# 			line.reconcile=False

	@api.onchange('taxes')
	def onchange_taxes(self):

		if self.amount>0:

			tax_link = []
			r = []
			delete = []

			t_invoice = 100
			t_sales_tax=0
			t_sales_tax_withheld=0
			t_total_amount=0
			t_witholding_tax=0
			t_total_withheld=0
			t_paid=0
			t_percentage=""
			rate_income_tax = 0
			rate_st = 0
			rate_withholding_st = 0

			t_taxable_amount = 0

			delete = delete.append(2)
			self.tax_link = delete
			for taxx in self.taxes:
				if taxx.wh_type == "income_tax":
					rate_income_tax = taxx.amount
				if taxx.wh_type == "sales_tax":
					rate_st = taxx.amount 
					rate_withholding_st = taxx.child_ids.amount 
				t_sales_tax = rate_st * t_invoice
				t_sales_tax_withheld = t_sales_tax * rate_withholding_st
				t_total_amount = t_invoice + t_sales_tax
				t_witholding_tax = rate_income_tax * t_total_amount
				t_total_withheld = t_sales_tax_withheld + t_witholding_tax
				t_paid = t_total_amount - t_total_withheld
			if t_paid > 0:
				t_percentage = t_total_withheld/t_paid

			for x in self.taxes:

				r.append({

					'name':x.name,
					'account_id':x.account_collected_id.id,
					'payment_link':self.id,                   

					})

			self.tax_link = r
			r=[]
			
	@api.depends('tax_link')
	def tax_total(self):
		self.t_total = 0.0
		for x in self.tax_link:
			self.t_total = x.amount + self.t_total

		self.t_total                

	# @api.depends('customer_tree')
	# def invoice_total(self):
	# 	self.total = 0.0
	# 	for x in self.customer_tree:
	# 		self.total = x.due_amount + self.total

	# 	self.total

	@api.multi
	def journal_entry_with_tax_payments(self,debit_account,credit_account,debit_amount,credit_amount):
		self.state = 'post'
		# for x in self.customer_tree:
		# 	if x.reconcile == True:
		# 		x.invoice_id.write({'state':"paid"})



		journal_entries = self.env['account.move'].search([('id','=',self.journal_entry_id.id)])
		journal_entries_lines = self.env['account.move.line'].search([])
		if not journal_entries:	
			create_journal_entry = journal_entries.create({
					'journal_id': self.journal_id.id,
					'date':self.date,
					'id': self.journal_entry_id.id,
					'ref' : self.reference,
					# 'branch': self.branch.id,
					# 'firm_partner':self.firm_partner.id,
					# 'tagm_entity':self.tagm_entity.id							
					})

			self.journal_entry_id = create_journal_entry.id



			b=journal_entries_lines.create({
				'account_id':debit_account,
				'partner_id':self.partner_id.id,
				'name':self.partner_id.name,
				'debit':0.0,
				'credit':0.0,
				'move_id':create_journal_entry.id,
				'identify' : 'd'
				})
			journal_entries_lines.create({
				'account_id':credit_account,
				'partner_id':self.partner_id.id,
				'name':self.partner_id.name,
				'credit':0.0,
				'debit':0.0,
				'move_id':create_journal_entry.id,
				'identify' : 'c'
				})


		journal_entries = self.env['account.move'].search([('id','=',self.journal_entry_id.id)])
		for line in journal_entries.line_ids:
			if line.identify=='d':
				line.credit = 0
				line.debit = debit_amount
			elif line.identify=='c':
				line.debit = 0
				line.credit = credit_amount


		for x in self.tax_link:
			if self.receipts == True:
				create_tax = journal_entries.line_id.create({
				'account_id':x.account_id.id,    
				'partner_id':self.partner_id.id,
				'name':x.name,
				'credit':0,
				'debit' :x.amount,
				'move_id':journal_entries.id
				})
			else:
				create_tax = journal_entries.line_id.create({
				'account_id':x.account_id.id,    
				'partner_id':self.partner_id.id,
				'name':x.name,
				'credit':x.amount,
				'debit' :0,
				'move_id':journal_entries.id
				})
	@api.multi
	def journal_entry_with_tax(self):
		if self.receipts == True:
			debit_account = self.journal_id.default_debit_account_id.id
			credit_account = self.partner_id.property_account_receivable_id.id
			debit_amount = self.amount
			credit_amount = self.amount +self.t_total
		else:
			debit_account = self.partner_id.property_account_payable_id.id
			credit_account = self.journal_id.default_credit_account_id.id
			debit_amount = self.amount +self.t_total
			credit_amount = self.amount

		self.journal_entry_with_tax_payments(debit_account,credit_account,debit_amount,credit_amount)

		cash_registers = self.env['account.bank.statement'].search([('state','=','open')])
		for line in cash_registers:
			if self.receipts:
				line.randp_ids.create({
					'date':self.date,
					'partner_id':self.partner_id.id,
					'reference':self.reference,
					'amount':self.amount,
					'cash_reg_id' : line.id,
					'cus_pay_bc_id' : self.id,
					})
			else:
				line.randp_ids.create({
					'date':self.date,
					'partner_id':self.partner_id.id,
					'reference':self.reference,
					'amount':self.amount * -1,
					'cash_reg_id' : line.id,
					'cus_pay_bc_id' : self.id,
					})


		if self.receipts == True:
			inv_amount = 0
			pay_amount = self.amount
			invoices = self.env['account.invoice'].search([('state','=',"open"),('type','=','out_invoice'),('partner_id.id','=',self.partner_id.id)])
			ids=[]
			for inv in invoices:
				ids.append(inv.id)
			sorted_inv_ids = sorted(ids)

			for inv_id in sorted_inv_ids:
				record = self.env['account.invoice'].search([('id','=',inv_id)])
				record.write({'state':'paid'})
				inv_amount = record.amount_total
				if pay_amount > record.amount_total:
					pay_amount -= record.amount_total
					inv = []
					inv.append({
					'date':self.date,
					'amount':record.amount_total,
					'pay_id':self.id,
					'pay_tree_id':inv_id,
					})
					record.pay_tree_id = inv
					record.write({'state':'paid'})
				elif pay_amount <= record.amount_total:
					inv = []
					inv.append({
					'date':self.date,
					'amount':pay_amount,
					'pay_id':self.id,
					'pay_tree_id':inv_id,
					})
					record.pay_tree_id = inv
					record.write({'state':'paid'})
					break

		# if self.receipts == True:
		# 	invoices = self.env['account.invoice'].search([('state','=',"open"),('type','=','out_invoice'),('partner_id.id','=',self.partner_id.id)])
		# 	for x in invoices:
		# 		for y in self.customer_tree:
		# 			if x.number == y.invoice_id.number:

		# 				inv = []
		# 				inv.append({
		# 					'date':y.date,
		# 					'amount':y.reconciled_amount,
		# 					'pay_id':self.id,
		# 					'pay_tree_id':x.id,
		# 					})

		# 				x.pay_tree_id = inv
		# 				x.residual = x.residual - x.pay_tree_id.amount
		# 				if x.residual == 0.00:
		# 					x.write({'state':'paid'})

					
	@api.multi
	def cancel_voucher_bcube(self):
		self.state = 'draft'
		journal_entries = self.env['account.move'].search([('id','=',self.journal_entry_id.id)])
		journal_entries_lines = self.env['account.move.line'].search([])

		if journal_entries:
			journal_entries.unlink()

		# for x in self.customer_tree:
		# 	if x.reconcile == True:
		# 		x.invoice_id.write({'state':"open"})

		invoices = self.env['account.invoice'].search([('state','=',"open"),('type','=','out_invoice'),('partner_id.id','=',self.partner_id.id)])
		for x in invoices:
			if x.pay_tree_id.pay_id.number == self.number:
				x.pay_tree_id.unlink()
				x.write({'state':"open"})


		
class AccountMoveRemoveValidation(models.Model):
	_inherit = "account.move"
	@api.multi
	def assert_balanced(self):
		if not self.ids:
						return True
		prec = self.env['decimal.precision'].precision_get('Account')

		self._cr.execute("""\
						SELECT      move_id
						FROM        account_move_line
						WHERE       move_id in %s
						GROUP BY    move_id
						HAVING      abs(sum(debit) - sum(credit)) > %s
						""", (tuple(self.ids), 10 ** (-max(5, prec))))
		
		return True

class AccountMoveLineInher(models.Model):
	_inherit = "account.move.line"

	identify = fields.Char('Identify')

class taxtest(models.Model):
	_inherit = "account.tax"

	with_holding = fields.Boolean('Withholding')


	wh_type =fields.Selection([
		('income_tax', 'Income Tax'),('sales_tax','Sales Tax'),],
		 string='Withholding Type',default='income_tax')

class CustomerPaymentTree(models.Model):

	_name = 'customer.payment.tree'
	
	invoice =fields.Char('Invoice #')
	date=fields.Date('Date')
	due_amount =fields.Float('Due Amount')
	reconcile = fields.Boolean('Reconcile')
	reconciled_amount=fields.Float('Reconciled Amount')
	customer_payment_link=fields.Many2one('customer.payment.bcube')
	invoice_id=fields.Many2one('account.invoice')

	@api.multi
	@api.constrains('reconciled_amount','due_amount')
	def _check_reconciliation(self):
		if self.reconciled_amount > self.due_amount:
			raise ValidationError('Reconciled Amount is not Correct')


	@api.onchange('due_amount','reconciled_amount')
	def reconcile_tick(self):
		if self.due_amount == self.reconciled_amount:
			self.reconcile = True

class Coustomer_Tax(models.Model):
	_inherit = 'account.invoice.tax'

	payment_link = fields.Many2one('customer.payment.bcube')

class ABSModification(models.Model):
	_inherit = 'account.bank.statement'
	bcube_pid 			= fields.Many2one('res.partner', 'Partner')
	randp_ids		    = fields.One2many('receipts.and.payment', 'cash_reg_id')
	receipts_amount     = fields.Float(compute='_compute_amount',string="Receipt")

	def _compute_amount(self):
		self.receipts_amount = sum(line.amount for line in self.randp_ids if line.amount > 0)

class ABSModification(models.Model):
	_name = 'receipts.and.payment'
	date 				= fields.Date('Date')
	communication	    = fields.Char('Communication')
	partner_id		    = fields.Many2one('res.partner', 'Partner')
	reference		    = fields.Char('Reference')
	amount  		    = fields.Float('Amount')
	cash_reg_id		    = fields.Many2one('account.bank.statement','Cash Reg Id', ondelete='cascade')
	cus_pay_bc_id		= fields.Many2one('customer.payment.bcube','CustomerPayment Id', ondelete='cascade')
