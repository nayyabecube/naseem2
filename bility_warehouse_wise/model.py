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
    _name = 'report.bility_warehouse_wise.customer_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('bility_warehouse_wise.customer_report')
        active_wizard = self.env['bility.warehouse'].search([])
        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['bility.warehouse'].search([('id','=',emp_list_max)])

        record_wizard_del = self.env['bility.warehouse'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()


        date_from = record_wizard.date_from
        date_to = record_wizard.date_to
        warehouse_id = record_wizard.warehouse_id

        
        records = []
        rec = self.env['stock.picking'].search([('state','=','done')])
        for x in rec:
            if x.picking_type_id.warehouse_id.id == warehouse_id.id:
                if "Delivery" in x.picking_type_id.name:
                    data = self.env['mail.tracking.value'].search([('mail_message_id.res_id','=',x.id)])
                    if data:
                        for z in data:
                            if z.field == 'state' and z.new_value_char == 'Done':
                                if str(z.mail_message_id.date[:10]) >= date_from and str(z.mail_message_id.date[:10]) <= date_to:
                                    records.append(x)




        def get_cat(attr):
            value = 0
            rec = self.env['stock.picking'].search([('id','=',attr)])
            for x in rec:
                for y in x.pack_operation_product_ids:
                    value = value + y.product_qty

            return value





        docargs = {
        
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'date_from': date_from,
            'date_to': date_to,
            'warehouse_id': warehouse_id.name,
            'records': records,
            'get_cat': get_cat,
    
            }

        return report_obj.render('bility_warehouse_wise.customer_report', docargs)