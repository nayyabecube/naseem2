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
    _name = 'report.customer_minimum_sale.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('customer_minimum_sale.customer_report')
        active_wizard = self.env['customer.lowselling'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['customer.lowselling'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['customer.lowselling'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        date = record_wizard.date



        records = []
        start_date = datetime.strptime(date,"%Y-%m-%d")
        rec = self.env['res.partner'].search([('customer','=',True)])
        for x in rec:
            new_date = start_date - relativedelta(days=x.associated_days)
            new_date = str(new_date)
            new_date = str(new_date[:10])
            value = 0
            value1 = 0
            summed = 0
            data = self.env['account.invoice'].search([('type','=','out_invoice'),('state','not in',['draft','cancel']),('date_invoice','>=',new_date),('date_invoice','<=',date),('partner_id','=',x.id)])
            for z in data:
                value = value + z.amount_total

            enteries = self.env['account.invoice'].search([('type','=','out_refund'),('state','not in',['draft','cancel']),('date_invoice','>=',new_date),('date_invoice','<=',date),('partner_id','=',x.id)])
            for y in enteries:
                value1 = value1 + y.amount_total


            summed = value - value1
            if  summed < x.minimum_sale:
                records.append(x)


        def get_sold(attr,num):
            start_date = datetime.strptime(date,"%Y-%m-%d")
            new_date = start_date - relativedelta(days=num)
            new_date = str(new_date)
            new_date = str(new_date[:10])
            value = 0
            data = self.env['account.invoice'].search([('type','=','out_invoice'),('state','not in',['draft','cancel']),('date_invoice','>=',new_date),('date_invoice','<=',date),('partner_id','=',attr)])
            for z in data:
                value = value + z.amount_total

            return value



        def get_diff(attr,num):
            start_date = datetime.strptime(date,"%Y-%m-%d")
            new_date = start_date - relativedelta(days=num)
            new_date = str(new_date)
            new_date = str(new_date[:10])
            value = 0
            value1 = 0
            summed = 0
            data = self.env['account.invoice'].search([('type','=','out_invoice'),('state','not in',['draft','cancel']),('date_invoice','>=',new_date),('date_invoice','<=',date),('partner_id','=',attr)])
            for z in data:
                value = value + z.amount_total

            enteries = self.env['account.invoice'].search([('type','=','out_refund'),('state','not in',['draft','cancel']),('date_invoice','>=',new_date),('date_invoice','<=',date),('partner_id','=',attr)])
            for y in enteries:
                value1 = value1 + y.amount_total


            summed = value - value1
            

            return summed




        docargs = {
        
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'date': date,
            'records': records,
            'get_sold': get_sold,
            'get_diff': get_diff,
    
            }

        return report_obj.render('customer_minimum_sale.customer_report', docargs)