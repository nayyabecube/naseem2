# -*- coding: utf-8 -*-

from openerp import models, fields, api

class SupplierAdjustments(models.Model):
    _name = 'supplier.adjustments'
    partner_id = fields.Many2one('res.partner',string="Supplier " , required = True)
    date = fields.Date(string="Date ", required = True)
    # adjustment_type = fields.Selection([
    #     ('local', 'Local'),
    #     ('fc', 'FC'),
    #     ('both', 'Both'),
    #     ],string = "Adjustment Type", default = 'local')
    dc_type = fields.Selection([
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ],string = "Select Type", required=True)
    amount = fields.Float(string="Amount PKR")
    fc_amount = fields.Float(string="FC Amount")
    conversion_rate = fields.Float(string="Conversion Rate ")
    currency = fields.Many2one('res.currency',string="Currency ")
    remarks = fields.Char(string="Remarks ")
    account_head = fields.Many2one('account.account', string="Account Head ", required = True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ],string = "Stages", default = 'draft')

    journal = fields.Many2one('account.journal', string="Journal ")
    move_id = fields.Many2one('account.move', string="Entry Link ")

    @api.one
    def validateRecord(self):
    	self.write({'state':'validate'})
        self.createJournalEntries()
    @api.one
    def setToDraft(self):
    	self.write({'state':'draft'})

    @api.onchange('fc_amount','conversion_rate')
    def get_amount_pkr(self):
        self.amount = self.fc_amount * self.conversion_rate


    @api.onchange('journal')
    def get_account(self):
        self.account_head = self.journal.default_debit_account_id.id




    @api.multi
    def genrateJournalEntries(self, credit_acc, debit_acc, partner_id, journal_id, date, amount,fc_amount,description):
        JornalEntries = self.env['account.move']
        JornalEntries_lines = self.env['account.move.line']
        create_journal_entry = JornalEntries.create({
                'journal_id': journal_id,
                'date':date,
                'supplier_adjustments_id': self.id, # field to link the record
                })
        create_journal_entry.line_ids.create({
            'account_id':debit_acc,
            'partner_id':partner_id,
            'name': description, 
            'debit':amount,
            'fc_amount':fc_amount,
            'move_id':create_journal_entry.id
            })
        create_journal_entry.line_ids.create({
            'account_id':credit_acc,
            'partner_id':partner_id,
            'name':description,   
            'credit':amount,
            'fc_amount':fc_amount,
            'move_id':create_journal_entry.id
            })
        self.move_id = create_journal_entry.id

    @api.multi
    def createJournalEntries(self):
        journal_id = self.journal
        if self.move_id:
            move_id.unlink()
        # if self.amount > 0:
        #     self.genrateJournalEntries(self.partner_id.property_account_payable_id.id,
        #         self.account_head.id,
        #         self.partner_id.id, journal_id.id,self.date, self.amount
        #         )
        # else:
        #     self.genrateJournalEntries(self.account_head.id,
        #         self.partner_id.property_account_payable_id.id,
        #         self.partner_id.id, journal_id.id,self.date, self.amount
        #         )
        if self.dc_type == 'credit':
            self.genrateJournalEntries(self.partner_id.property_account_payable_id.id,
                self.account_head.id,
                self.partner_id.id, journal_id.id,self.date, self.amount,self.fc_amount,self.remarks
                )
        else:
            self.genrateJournalEntries(self.account_head.id,
                self.partner_id.property_account_payable_id.id,
                self.partner_id.id, journal_id.id,self.date, self.amount,self.fc_amount,self.remarks
                )
        return True

    # @api.multi
    # def write(self, vals):
    #     Res = super(SupplierAdjustments,self).write(vals)
    #     old_rec = self.env['account.move'].search([('supplier_adjustments_id','=',self.id)])
    #     if old_rec:
    #         for rec in old_rec:
    #             rec.unlink()
    #     self.createJournalEntries()
    #     return Res
