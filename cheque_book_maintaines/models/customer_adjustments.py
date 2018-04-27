# -*- coding: utf-8 -*-

from openerp import models, fields, api

class BankAdjustmentsCheque(models.Model):
    _name = 'bank.adjustments.cheque'
    partner_id = fields.Many2one('res.partner',string="Customer ")
    date = fields.Date(string="Date ")
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ],string = "Type", default = 'customer')
    dc_type = fields.Selection([
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ],string = "Select Type", required=True)
    amount = fields.Float(string="Amount ")
    remarks = fields.Char(string="Remarks ")
    account_head = fields.Many2one('account.account', string="Account Head ")
    journal = fields.Many2one('account.journal', string="Journal ")
    move_id = fields.Many2one('account.move', string="Entry Link ")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ],string = "Stages", default = 'draft')

    @api.one
    def validateRecord(self):
    	self.write({'state':'validate'})
        self.createJournalEntries()
    @api.one
    def setToDraft(self):
    	self.write({'state':'draft'})


    @api.onchange('journal')
    def get_account(self):
        self.account_head = self.journal.default_debit_account_id.id





    @api.multi
    def genrateJournalEntries(self, credit_acc, debit_acc, partner_id, journal_id, date, amount):
        JornalEntries = self.env['account.move']
        JornalEntries_lines = self.env['account.move.line']
        create_journal_entry = JornalEntries.create({
                'journal_id': journal_id,
                'date':date,
                'bank_adjustments_id': self.id, # field to link the record
                })
        create_journal_entry.line_ids.create({
            'account_id':debit_acc,
            'partner_id':partner_id,
            'name': 'Debit', 
            'debit':amount,
            'move_id':create_journal_entry.id
            })
        create_journal_entry.line_ids.create({
            'account_id':credit_acc,
            'partner_id':partner_id,
            'name':'Credit',   
            'credit':amount,
            'move_id':create_journal_entry.id
            })
        self.move_id = create_journal_entry.id
    @api.multi
    def createJournalEntries(self):
        if self.move_id:
            self.move_id.unlink()
        journal_id = self.journal
        # if self.amount > 0:
        #     self.genrateJournalEntries(self.account_head.id,
        #         self.partner_id.property_account_receivable_id.id,
        #         self.partner_id.id, journal_id.id,self.date, self.amount
        #         )
        # else:
        #     self.genrateJournalEntries(self.partner_id.property_account_receivable_id.id,
        #         self.account_head.id,
        #         self.partner_id.id, journal_id.id,self.date, self.amount
        #         )
        if self.dc_type == 'debit':
            self.genrateJournalEntries(self.account_head.id,
                self.partner_id.property_account_receivable_id.id,
                self.partner_id.id, journal_id.id,self.date, self.amount
                )
        else:
            self.genrateJournalEntries(self.partner_id.property_account_receivable_id.id,
                self.account_head.id,
                self.partner_id.id, journal_id.id,self.date, self.amount
                )
        
        return True

    # @api.multi
    # def write(self, vals):
    #     Res = super(BankAdjustmentsCheque,self).write(vals)
    #     old_rec = self.env['account.move'].search([('bank_adjustments_id','=',self.id)])
    #     if old_rec:
    #         for rec in old_rec:
    #             rec.unlink()
    #     self.createJournalEntries()
    #     return Res
