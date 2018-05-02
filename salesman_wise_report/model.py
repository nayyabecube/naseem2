#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################
from openerp import models, fields, api
from datetime import timedelta,datetime,date
from dateutil.relativedelta import relativedelta
import time

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.salesman_wise_report.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('salesman_wise_report.customer_report')
        active_wizard = self.env['sales.man'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['sales.man'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['sales.man'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        date_from = record_wizard.date_from
        date_to = record_wizard.date_to
        sales_id = record_wizard.sales_id
        sales = record_wizard.sales
        receipts = record_wizard.receipts
        returns = record_wizard.returns
        profit = record_wizard.profit
        b_types = record_wizard.b_types


        if b_types == "all":
            salesman = []
            rec = self.env['res.users'].search([])
            for x in rec:
                salesman.append(x)

        if b_types == "specfic":
            salesman = []
            for x in sales_id:
                salesman.append(x)


        
        if sales == True or profit == True:
            records = []
            def get_record(attr):
                del records[:]
                rec = self.env['account.invoice'].search([('type','=','out_invoice'),('state','not in',['draft','cancel']),('date_invoice','>=',date_from),('date_invoice','<=',date_to),('user_id','=',attr)])
                for x in rec:
                    records.append(x)


        if returns == True:
            records = []
            def get_record(attr):
                del records[:]
                rec = self.env['account.invoice'].search([('type','=','out_refund'),('state','not in',['draft','cancel']),('date_invoice','>=',date_from),('date_invoice','<=',date_to),('user_id','=',attr)])
                for x in rec:
                    records.append(x)

        if receipts == True:
            records = []
            def get_record(attr):
                del records[:]
                rec = self.env['customer.payment.bcube'].search([('state','=','post'),('date','>=',date_from),('date','<=',date_to),('sales_id','=',attr),('receipts','=',True)])
                for x in rec:
                    records.append(x)


        def opt_check():
            num = 0
            if receipts == True:
                num = 0
            else:
                num = 1

            return num


        def get_check():
            num = " "
            if receipts == True:
                num = "Receipts"
            if sales == True:
                num = "Sales"
            if profit == True:
                num = "Profit"
            if returns == True:
                num = "Returns"

            return num

        

        

        docargs = {
        
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'date_from': date_from,
            'date_to': date_to,
            'salesman': salesman,
            'records': records,
            'get_record': get_record,
            'opt_check': opt_check,
            'get_check': get_check,
    
            }

        return report_obj.render('salesman_wise_report.customer_report', docargs)