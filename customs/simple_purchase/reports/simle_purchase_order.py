from odoo import models, fields, api
import datetime, pytz


class PurchaseOrder(models.AbstractModel):
    _name = 'report.simple_purchase.all_purchase_order_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        pos = self.env['purchases.order'].search([])

        return {
            'pos': pos,
            'docs': docids,
            'current_date': fields.date.today()
        }
