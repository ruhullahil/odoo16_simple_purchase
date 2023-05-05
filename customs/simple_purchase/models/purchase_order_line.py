from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _name = 'purchases.order.line'
    _description = 'Purchase Order Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one('product.product', string='Product', required=True, tracking=True)
    quantity = fields.Float(string='Quantity', required=True, tracking=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id')
    unit_price = fields.Float(string='Unit Price', tracking=True)
    price_total = fields.Float(string='Total', compute='_get_price_total', store=True, tracking=True)
    order_id = fields.Many2one('purchases.order', )

    @api.depends('unit_price', 'quantity')
    def _get_price_total(self):
        for rec in self:
            rec.price_total = rec.quantity * rec.unit_price
