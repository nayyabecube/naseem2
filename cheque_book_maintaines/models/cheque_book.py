# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ChkBook(models.Model):
    _name = 'cheque.book.maintain'
    _rec_name = 'acct_no'

    acct_no = fields.Char('Account No.')
    t_amount =  fields.Float('Total Amount')
    bank = fields.Many2one('account.account',string="Bank Name")
    cheque_frm_num = fields.Integer(string="Cheque No From.")
    cheque_frm_descp = fields.Char(string="Cheque Detail.")
    cheque_to_num = fields.Integer(string="Cheque No T.")
    cheque_to_descp = fields.Char(string="Cheque No Detail.")
    cheque_lev = fields.Integer(string="Cheque Leaves.")
    rem_lev = fields.Integer(string="Remainig Leaves.")
    # fst_cheque_no = fields.Integer(string="First Cheque No.")
    cheque_tree_id = fields.One2many('cheque.book.tree','chk_tree')
    stages = fields.Selection([
        ('ongoing', 'On Going'),
        ('completed', 'Completed'),
        ],string = "Stages", default = 'ongoing')

    @api.onchange('cheque_frm_num','cheque_to_num')
    def _onchangeChequeNo(self):
        if self.cheque_frm_num or self.cheque_to_num:
            self.cheque_lev = self.cheque_to_num - self.cheque_frm_num

    # @api.onchange('bank')
    # def _onchangeChequeBank(self):
    #     if self.bank:
    #         self.acct_no = self.bank.custom_acc_no

    @api.multi
    def genrate_leaves(self):
        if self.cheque_lev:
            for leaves in self.cheque_tree_id:
                leaves.unlink()
            new = self.cheque_frm_num
            cheque_no = str(self.cheque_frm_descp) + str(new)
            for x in range(self.cheque_lev):
                records = self.env['cheque.book.tree'].create({
                    'tree_cheque_no':cheque_no,
                    'chk_tree':self.id,
                    'bank':self.bank.id,
                    })
                new = new + 1
                cheque_no = str(self.cheque_frm_descp) + str(new) 


    @api.multi
    def cheque_completed(self):
        self.write({'stages':'completed'})

class ChkBookTree(models.Model):
    _name = 'cheque.book.tree'
    _rec_name = 'tree_cheque_no'

    date = fields.Date()
    tree_cheque_no = fields.Char(string="Cheque No.")
    amount =  fields.Float('Total Amount')
    desc =  fields.Char('Description')
    pay_ref =  fields.Char('Payment Reference')
    cancel =  fields.Boolean('Cancel')
    issued =  fields.Boolean('Issued')
    bank = fields.Many2one('account.account',string="Bank Name")
    # received =  fields.Char('Received By.')

    chk_tree = fields.Many2one('cheque.book.maintain')


class bank(models.Model):
    _name = 'bank.bank'
    name = fields.Char()

