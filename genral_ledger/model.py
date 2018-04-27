#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning

class PartnerLedgerReport(models.AbstractModel):
    _name = 'report.genral_ledger.genral_ledger_report'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('genral_ledger.genral_ledger_report')
        active_wizard = self.env['genral.ledger'].search([])
        records = self.env['account.account'].browse(docids)
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['genral.ledger'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['genral.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        typed = record_wizard.entry_type
        account = record_wizard.account

        def opening(bal):
            if typed == "all":
                opend = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',bal.id)])

            if typed == "posted":
                opend = self.env['account.move.line'].search([('move_id.date','<',form),('account_id.id','=',bal.id),('move_id.state','=',"posted")])

            debit = 0
            credit = 0
            opening = 0
            for x in opend:
                debit = debit + x.debit
                credit = credit + x.credit

            if bal.nature == 'debit':
                opening = debit - credit

            if bal.nature == 'credit':
                opening = credit - debit

            return opening
        
        if typed == "all":
            entries = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','=',account.id)])

        if typed == "posted":
            entries = self.env['account.move.line'].search([('move_id.date','>=',form),('move_id.date','<=',to),('account_id.id','=',account.id),('move_id.state','=',"posted")])
            
        docargs = {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': account,
            'data': data,
            'form': form,
            'to': to,
            'opening': opening,
            'entries': entries,
        }

        return report_obj.render('genral_ledger.genral_ledger_report', docargs)