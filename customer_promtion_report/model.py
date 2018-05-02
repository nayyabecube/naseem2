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
    _name = 'report.customer_promtion_report.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('customer_promtion_report.customer_report')
        active_wizard = self.env['customer.promt'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['customer.promt'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['customer.promt'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        date_from = record_wizard.date_from
        date_to = record_wizard.date_to
        supplier_id = record_wizard.supplier_id
        state = record_wizard.state
        b_types = record_wizard.b_types


        if b_types == "all":
            salesman = []
            rec = self.env['res.partner'].search([('customer','=',True)])
            for x in rec:
                salesman.append(x)



        if b_types == "specfic":
            salesman = []
            for x in supplier_id:
                salesman.append(x)


        
        records = []
        def get_record(attr):
            del records[:]
            rec = self.env['promo.customer'].search([('stages','=',state),('date','>=',date_from),('date','<=',date_to),('customer','=',attr)])
            for x in rec:
                records.append(x)




        

        docargs = {
        
            'doc_ids': docids,
            'doc_model': 'promo.customer',
            'date_from': date_from,
            'date_to': date_to,
            'state': state,
            'records': records,
            'salesman': salesman,
            'get_record': get_record,
    
            }

        return report_obj.render('customer_promtion_report.customer_report', docargs)