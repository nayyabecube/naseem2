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
    _name = 'report.supplier_purchase_report.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('supplier_purchase_report.customer_report')
        active_wizard = self.env['supplier.purchase'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['supplier.purchase'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['supplier.purchase'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        date_from = record_wizard.date_from
        date_to = record_wizard.date_to
        supplier_id = record_wizard.supplier_id
        b_types = record_wizard.b_types


        if b_types == "all":
            salesman = []
            rec = self.env['res.partner'].search([('supplier','=',True)])
            for x in rec:
                salesman.append(x)



        if b_types == "specfic":
            salesman = []
            for x in supplier_id:
                salesman.append(x)


        
        records = []
        def get_record(attr):
            del records[:]
            rec = self.env['account.invoice.line'].search([('invoice_id.type','=','in_invoice'),('invoice_id.state','not in',['draft','cancel']),('invoice_id.date_invoice','>=',date_from),('invoice_id.date_invoice','<=',date_to),('invoice_id.partner_id','=',attr)])
            for x in rec:
                if x.product_id not in records:
                    records.append(x.product_id)


        def get_qty(attr):
            value = 0
            rec = self.env['account.invoice.line'].search([('invoice_id.type','=','in_invoice'),('invoice_id.state','not in',['draft','cancel']),('invoice_id.date_invoice','>=',date_from),('invoice_id.date_invoice','<=',date_to),('product_id','=',attr)])
            for x in rec:
                value = value + x.quantity


            return value


        

        

        docargs = {
        
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'date_from': date_from,
            'date_to': date_to,
            'records': records,
            'salesman': salesman,
            'get_record': get_record,
            'get_qty': get_qty,
    
            }

        return report_obj.render('supplier_purchase_report.customer_report', docargs)