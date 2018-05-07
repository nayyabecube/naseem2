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

class customerinvoicereport(models.AbstractModel):
    _name = 'report.purchase_order_report.purchase_order_report_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('purchase_order_report.purchase_order_report_report')
        records = self.env['purchase.order'].browse(docids)


        def get_name():
            value = " "
            if records.state == "draft":
                value = "Quotation Order"
            if records.state == "purchase":
                value = "Purchase Order"
            if records.state != "purchase" and records.state != "draft":
                value = "Invoice"


            return value



        docargs = {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': records,
            'get_name': get_name,
            }

        return report_obj.render('purchase_order_report.purchase_order_report_report', docargs)