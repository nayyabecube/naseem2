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

class saleswizard_report(models.AbstractModel):
    _name = 'report.saleswizard_report.saleswizard_report_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('saleswizard_report.saleswizard_report_report')
        records = self.env['naseem.sales.promo'].browse(docids)


        def get_type():
            num = 0
            if records.scheme_type == "instant_promo":
                num = 1
            if records.scheme_type == "percentage_disc":
                num = 2
            if records.scheme_type == "product_scheme":
                num = 3
            if records.scheme_type == "points_scheme":
                num = 4


            return num


        def get_app():
            value = 0
            if records.applicable_on == "product":
                value = 1
            if records.applicable_on == "category":
                value = 2

            return value






        docargs = {
            'doc_ids': docids,
            'doc_model': 'naseem.sales.promo',
            'docs': records,
            'get_type': get_type,
            'get_app': get_app,
            }

        return report_obj.render('saleswizard_report.saleswizard_report_report', docargs)