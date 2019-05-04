# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class MrpShift(models.Model):
    """Added Manufacture Shifts."""

    _name = 'mrp.shift'
    _description = "Manufacture Shift"
    _inherit = ['mail.thread']

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_id = self.env['stock.warehouse'].search([
            ('company_id', '=', company)], limit=1)
        return warehouse_id

    @api.depends('session_ids')
    def _compute_current_session(self):
        for shift in self:
            session = shift.session_ids.filtered(
                lambda r: r.user_id.id == self.env.uid and
                not r.state == 'closed' and not r.rescue)
            # sessions ordered by id desc
            shift.current_session_id = session and session[0].id or False

    @api.depends('session_ids')
    def _compute_last_session(self):
        session = self.env['mrp.shift.session']
        for shift in self:
            session = session.search([
                ('shift_id', '=', shift.id),
                ('state', '=', 'closed')],
                order="stop_at desc", limit=1)
            # sessions ordered by closing date desc
            shift.last_session_id = session and session.id or False

    name = fields.Char(
        string='Shift Name', required=True)
    code = fields.Char(
        string='Short Code', size=5, required=True,
        help="The shift sessions of will be named using this prefix.")
    sequence_id = fields.Many2one(
        'ir.sequence', string='Session Sequence', readonly=True, copy=False,
        help="This field contains the information related to the numbering of the shift sessions"
    user_id = fields.Many2one(
        'res.users', string='Responsible', track_visibility='onchange',
        help='Person responsible for this shift')
    session_ids = fields.One2many(
        'mrp.shift.session', 'shift_id', string='Sessions',
        help="")
    current_session_id = fields.Many2one(
        'mrp.shift.session', compute='_compute_current_session',
        string="Current Session", store=True, readonly=True, 
        help="Session currenlty in progress")
    last_session_id = fields.Many2one(
        'mrp.shift.session', compute='_compute_last_session',
        store=True, readonly=True, string="Last Session",
        help="Last session closed")
    last_session_closing_date = fields.Datetime(
        string="Last Shift End", 
        related="last_session_id.stop_at", readonly=True,
        help="Date on which the last session was closed")
    resource_calendar_id = fields.Many2one(
        string="Work Schedule", help="Shift working schedule.")
    warehouse_id = fields.Many2one(
        'stock.warehouse', required=True, default=_default_warehouse_id)
    company_id = fields.Many2one(
	'res.company', required=True,
	default=lambda self: self.env.user.company_id)


class MrpShiftSession(models.Model):
    """Added Manufacture Working Sessions."""

    _name = 'mrp.shift.session'
    _order = 'id desc'
    _description = 'Shift Session'

    shift_id = fields.Many2one(
        'mrp.shift', string='Shift',
        required=True, index=True,
        help="Working shift for which this session was opened")
    name = fields.Char(
        string='Session ID',
        required=True, readonly=True, default='/',
        help="Identificator according to the sequence that is configured"
        " in the shift")
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        required=True,
        index=True,
        readonly=True,
        default=lambda self: self.shift_id.user_id.id,
        help='Person responsible for this working session')
    start_at = fields.Datetime(
        string='Opening Date', readonly=True,
        help="Date when this session was opened")
    stop_at = fields.Datetime(
        string='Closing Date', readonly=True, copy=False)
        help="Date when this session was closed") 
    state = fields.Selection([
	('opened', 'In Progress'),	
	('closed', 'Closed'),
        ], string='Status', required=True, readonly=True,
        index=True, copy=False, default='opened',
        help="Indicate which shift is currently working")
    rescue = fields.Boolean(
        string='Recovery Session',
        readonly=True,
        copy=False,
        help="Auto-generated session for orphan orders, ignored in constraint")


class MrpShiftProduction(models.Model):
    """Added Manufacture Orders by Shift."""

    _name = 'mrp.shift.production'
    _description = 'Manufacture Orders by Shift'

    session_id = fields.Many2one(
        'mrp.shift.session', string='Session ID',
        required=True, index=True,
        help="Identificator according to the sequence that is configured"
        " in the shift")
    shift_id = fields.Many2one(
        'mrp.shift', related="session_id.shift_id",
        readonly=True, help="Working shift for which this session was opened")
    production_id = fields.Many2one(
        'mrp.production', 'Manufacturing Order')
    qty_production = fields.Float(
        'Quantity', default=0.0,
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already handled by this Manufacture"
        " Order in this session")
    qty_produced = fields.Float(
        'Quantity', default=0.0,
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already handled by this Manufacture"
        " Order in this session")
