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

class saleorderreport(models.AbstractModel):
    _name = 'report.sale_order_report.sale_order_report_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sale_order_report.sale_order_report_report')
        records = self.env['sale.order'].browse(docids)



        def get_name():
            value = " "
            if records.direct_invoice_check == False:
                if records.state == "draft":
                    value = "Quotation Order"
                if records.state == "sale":
                    value = "Sale Order"
                if records.state != "sale" and records.state != "draft":
                    value = "Invoice"
            if records.direct_invoice_check == True:
                value = "Direct Invoice"

            return value



        docargs = {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': records,
            'get_name': get_name,
            }

        return report_obj.render('sale_order_report.sale_order_report_report', docargs)