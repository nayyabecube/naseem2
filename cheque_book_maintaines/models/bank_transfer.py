# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

class BankTransferCheque(models.Model):
    _name = 'bank.transfer.cheque'
    name = fields.Char(string="Name ")
    amount = fields.Float(string="Amount ")
    date = fields.Date(string="Date ")
    bank = fields.Many2one('account.account', string="Bank ")
    ref = fields.Char(string="Ref ")
    customer = fields.Many2one('res.partner',string="Customer ")
    journal_entry_id = fields.Many2one('account.move',string="Entry Link ")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ('done', 'Done'),
        ],string = "Stages", default = 'draft')


    @api.multi
    def createEntry(self):

        unknownCustomer = self.env['res.partner'].search([('name','=','unknown')])
        journal = self.env['account.journal'].search([('type','=',"bank")])
        for rec in journal:
            jouranll = rec.id
        journal_entry_id = self.genrateJournalEntries(unknownCustomer.property_account_receivable_id.id,
            self.bank.id, unknownCustomer.id, jouranll,
            self.date, self.amount, self.ref
         )
        old_rec = self.env['account.move'].search([('bank_transfer_id','=',self.id)])
        self.journal_entry_id = old_rec.id


    @api.one
    def validateRecord(self):
        if not self.customer:
            raise ValidationError('Please select customer before validation.')
    	self.write({'state':'validate'})
        old_rec = self.env['account.move'].search([('bank_transfer_id','=',self.id)])
        for rec in old_rec:
            # rec.button_cancel()
            for item in rec.line_ids:
                item.partner_id = self.customer.id
                # if item.debit > 0:
                #     item.debit = self.amount
                # if item.credit > 0:
                #     item.credit = self.amount
            rec.post()

    # @api.one
    # def cancel_entry(self):
    #     self.write({'state':'draft'})
    #     old_rec = self.env['account.move'].search([('bank_transfer_id','=',self.id)])
    #     for rec in old_rec:
    #         rec.button_cancel()
            # for item in rec.line_ids:
            #     item.partner_id = self.customer.id
            #     item.account_id = self.customer.property_account_receivable_id.id
            # rec.post()

    @api.one
    def setToDraft(self):
    	self.write({'state':'draft'})

    @api.one
    def setToDone(self):
        self.write({'state':'done'})

    @api.multi
    def genrateJournalEntries(self, credit_acc, debit_acc, partner_id, journal_id, date, amount,ref):
        JornalEntries = self.env['account.move']
        JornalEntries_lines = self.env['account.move.line']
        create_journal_entry = JornalEntries.create({
                'journal_id': journal_id,
                'date':date,
                'bank_transfer_id': self.id, # field to link the record
                })
        create_journal_entry.line_ids.create({
            'account_id':debit_acc,
            'partner_id':partner_id,
            'name': str(ref), 
            'debit':amount,
            'move_id':create_journal_entry.id
            })
        create_journal_entry.line_ids.create({
            'account_id':credit_acc,
            'partner_id':partner_id,
            'name':str(ref),   
            'credit':amount,
            'move_id':create_journal_entry.id
            })
        create_journal_entry.post()



    # @api.model
    # def create(self, vals):
    #     Res = super(BankTransferCheque,self).create(vals)
    #     unknownCustomer = self.env['res.partner'].search([('name','=','unknown')])
    #     journal_entry_id = Res.genrateJournalEntries(unknownCustomer.property_account_receivable_id.id,
    #         Res.bank.default_debit_account_id.id, unknownCustomer.id, Res.bank.id,
    #         Res.date, Res.amount, Res.ref
    #      )
    #     old_rec = self.env['account.move'].search([('bank_transfer_id','=',Res.id)])
    #     Res.journal_entry_id = old_rec.id
    #     return Res


    # @api.multi
    # def unlink(self, vals):
    #     Res = super(BankTransferCheque,self).unlink(vals)
    #     old_rec = self.env['account.move'].search([('bank_transfer_id','=',self.id)])
    #     for rec in old_rec:
    #         rec.button_cancel()
    #         rec.unlink(vals)
    #     return Res

    # @api.multi
    # def write(self, vals):
    #     Res = super(BankTransferCheque,self).write(vals)
    #     unknownCustomer = self.env['res.partner'].search([('name','=','unknown')])
        
    #     old_rec = self.env['account.move'].search([('bank_transfer_id','=',self.id)])
    #     for rec in old_rec:
    #         rec.unlink()
    #     self.genrateJournalEntries(self.bank.default_debit_account_id.id,
    #         unknownCustomer.property_account_receivable_id.id, unknownCustomer.id, self.bank.id,
    #         self.date, self.amount
    #      )
    #     return Res
