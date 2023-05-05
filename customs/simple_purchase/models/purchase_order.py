from odoo import fields, models, api
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _name = 'purchases.order'
    _description = 'Purchase Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', copy=False, required=True, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('purchase.order.seq'), tracking=True)
    date = fields.Date(required=True, tracking=True, string='Data')
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    order_line = fields.One2many('purchases.order.line', 'order_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('paid', 'Paid'),
    ], required=True, default='draft', tracking=True)
    amount_total = fields.Float(compute='_get_amount_total', store=True, tracking=True)
    journal_ids = fields.Many2many('account.move')

    @api.depends('order_line.price_total')
    def _get_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.order_line.mapped('price_total'))

    def _prepare_lines(self, account, debit=0, credit=0, partner=None, name=None):
        temp = {
            'account_id': account.id,
            'partner_id': partner.id,
            'name': name,
            'debit': debit,
            'credit': credit
        }
        return (0, 0, temp)

    def _prepare_confirm_accounting(self, po):
        self.ensure_one()
        journal_id = self.env['account.journal'].search([('name', 'ilike', 'Miscellaneous Operations')], limit=1,
                                                        order='id desc')
        debit_account = self.env['account.account'].search([('name', 'ilike', 'Stock Interim (Received)')], limit=1,
                                                           order='id desc')
        credit_account = self.env['account.account'].search([('name', 'ilike', 'Account Payable')], limit=1,
                                                            order='id desc')
        lines = list()
        lines.append(self._prepare_lines(debit_account, po.amount_total, 0, po.partner_id, po.name))
        lines.append(self._prepare_lines(credit_account, 0, po.amount_total, po.partner_id, po.name))
        move = {
            'ref': f'Journal of {po.name} for Confirm',
            'date': po.date,
            'journal_id': journal_id.id,
            'line_ids': lines,
            'company_id': self.env.company.id
        }
        return move

    def _prepare_paid_accounting(self, po):
        self.ensure_one()
        journal_id = self.env['account.journal'].search([('name', 'ilike', 'Miscellaneous Operations')], limit=1,
                                                        order='id desc')
        credit_account = self.env['account.account'].search([('name', 'ilike', 'Bank')], limit=1,
                                                            order='id desc')
        debit_account = self.env['account.account'].search([('name', 'ilike', 'Account Payable')], limit=1,
                                                           order='id desc')
        lines = list()
        lines.append(self._prepare_lines(debit_account, po.amount_total, 0, po.partner_id, po.name))
        lines.append(self._prepare_lines(credit_account, 0, po.amount_total, po.partner_id, po.name))
        move = {
            'ref': f'Journal of {po.name} for Paid',
            'date': po.date,
            'journal_id': journal_id.id,
            'line_ids': lines,
            'company_id': self.env.company.id
        }
        return move

    def btn_confirm(self):
        for rec in self:
            if rec.state not in ('confirm'):
                account_move = self.env['account.move'].sudo().create(rec._prepare_confirm_accounting(rec))
                if not account_move:
                    raise ValidationError('Something Went Wrong !! please Try again after some time')
                account_move.action_post()
                rec.journal_ids = [(4, account_move.id)]
                rec.state = 'confirm'

    def btn_paid(self):
        for rec in self:
            if rec.state not in ('paid'):
                account_move = self.env['account.move'].sudo().create(rec._prepare_paid_accounting(rec))
                if not account_move:
                    raise ValidationError('Something Went Wrong !! please Try again after some time')
                account_move.action_post()
                rec.journal_ids = [(4, account_move.id)]
                rec.state = 'paid'

    def action_view_journal(self):
        self.ensure_one()
        action_data = self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')
        action_data['domain'] = [('id', 'in', self.journal_ids.ids)]
        return action_data
