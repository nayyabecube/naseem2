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
##############################################################################
from openerp import models, fields, api

class LCCostingReport(models.AbstractModel):
    _name = 'report.customer_last_transaction.lc_costing_report_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('customer_last_transaction.lc_costing_report_report')
        records = self.env['res.partner'].browse(docids)



        def get_data(attr):
            value = 0
            l_date = []
            rec = self.env['account.invoice'].search([('partner_id','=',attr),('state','not in',['draft','cancel'])])
            for x in rec:
                if x.type == 'out_invoice' or x.type == 'out_refund':
                    l_date.append(x)
                    datelist = sorted(l_date, key=lambda x: x.date_invoice)
            new = datelist.pop().date_invoice
            for data in l_date:
                if data.date_invoice == new:
                    if data.type == "out_invoice":
                        value = value + data.amount_total
                    if data.type == "out_refund":
                        value = value + data.amount_total
                        value = value * -1


            return new,value

                   



        docargs = {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': records,
            'get_data': get_data,
            }

        return report_obj.render('customer_last_transaction.lc_costing_report_report', docargs)



class customerxtendlast(models.Model):
    _inherit = "res.partner"

    net = fields.Float('Net')