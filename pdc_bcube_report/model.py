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

class pdcbcubereport(models.AbstractModel):
    _name = 'report.pdc_bcube_report.pdc_bcube_report_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('pdc_bcube_report.pdc_bcube_report_report')
        records = self.env['pdc_bcube.pdc_bcube'].browse(docids)


        def get_rem():
            num = 0
            if records.stages == "settled":
                num = 1
            else:
                num = 0

            return num



        docargs = {
            'doc_ids': docids,
            'doc_model': 'pdc_bcube.pdc_bcube',
            'docs': records,
            'get_rem': get_rem,
            }

        return report_obj.render('pdc_bcube_report.pdc_bcube_report_report', docargs)