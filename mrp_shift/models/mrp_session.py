# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp


class MrpSession(models.Model):
    """Added Manufacture Working Sessions."""

    _name = 'mrp.session'
    _order = 'id desc'
    _description = 'Shift Session'
    _inherit = ['mail.thread']

    @api.depends('shift_id', 'workline_id', 'production_date')
    def _compute_name(self):
        for record in self:
            name = '/'
            if (record.shift_id and record.workline_id and
                    record.production_date):
                date = self.production_date.replace('-', '')[2:]
                name = '%s/%s/%s' % (
                    self.workline_id.code, date, self.shift_id.code)
            record.name = name

    name = fields.Char(
        string='Reference', compute='_compute_name', store=True,
        help="Unique identificator according to the shift, workline and"
        " Production date")
    shift_id = fields.Many2one(
        'mrp.shift', string='Shift',
        required=True, index=True,
        help="Working shift for which this session was opened")
    workline_id = fields.Many2one(
        'mrp.workline', string='Production Line', required=True,
        help="Production line that will be performed in this session")
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        required=True,
        index=True,
        readonly=True,
        default=lambda self: self.shift_id.user_id.id,
        help='Person responsible for this working session')
    production_date = fields.Date(
        required=True, default=fields.Date.today,
        help="Date at which production will be performed.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('produced', 'Produced'),
        ('closed', 'Closed'),
        ], string='Status', required=True, readonly=True,
        index=True, copy=False, default='draft',
        help="Indicate which shift is currently working")
    production_ids = fields.One2many(
        'mrp.session.line',
        'session_id', string='Manufacturing Orders',
        help="Show quantities produced by order in this session")

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Shift already exists !'),
    ]


class MrpSessionLine(models.Model):
    """Added detailed production performed in the Shift"""

    _name = 'mrp.session.line'
    _description = 'Manufacture Orders by Shift'

    @api.depends('production_id.product_qty')
    def _compute_qty_to_produce(self):
        """
        Compute the quantity to produce.
        """
        for record in self:
            production = record.production_id
            record.qty_to_produce = float_round(
                production.product_qty - production.qty_produced,
                precision_rounding=production.product_uom_id.rounding)

    @api.depends('production_id.product_qty', 'qty_produced')
    def _compute_is_produced(self):
        rounding = self.production_id.product_uom_id.rounding
        for record in self:
            record.is_produced = float_compare(
                record.qty_produced, record.production_id.product_qty,
                precision_rounding=rounding) >= 0

    @api.depends('session_id.name', 'production_id.name')
    def _compute_name(self):
        name = '/'
        for record in self:
            name = '/'
            if record.session_id and record.production_id:
                name = '%s - %s' % (
                    record.session_id.name, record.production_id.name)
            record.name = name

    name = fields.Char(
        'Description', compute='_compute_name', store=True)
    session_id = fields.Many2one(
        'mrp.session', string='Session ID',
        required=True, index=True,
        help="The shift where was produced the Manufacturing Order")
    production_id = fields.Many2one(
        'mrp.production', string='Manufacturing Order',
        required=True, index=True,
        help="Manufacturing Order produced in the selected shift")
    qty_to_produce = fields.Float(
        compute='_compute_qty_to_produce', string='Quantity To Produce',
        store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="Remaining quantity to complete this Manufacture Order")
    qty_produced = fields.Float(
        'Quantity Produced', default=0.0,
        readonly=True,
        help="The number of products already handled in the selected shift")

