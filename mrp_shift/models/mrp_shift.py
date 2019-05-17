# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class MrpShift(models.Model):
    """Added Manufacture Shifts."""

    _name = 'mrp.shift'
    _description = "Manufacture Shift"

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_id = self.env['stock.warehouse'].search([
            ('company_id', '=', company)], limit=1)
        return warehouse_id

    @api.multi
    def _compute_session_count(self):
        today = fields.Date.context_today(self)
        domains = {
            'count_session_draft': [('state', '=', 'draft')],
            'count_session_confirmed': [('state', '=', 'confirmed')],
            'count_session_produced': [('state', '=', 'produced')],
            'count_session_closed': [('state', '=', 'closed')],
            'count_session': [],
            'count_session_late': [
                ('production_date', '<', today),
                ('state', 'in', ['draft','confirmed', 'produced'])
            ],
            'count_session_today': [
                ('production_date', '=', today),
                ('state', 'in', ['draft','confirmed', 'produced'])
            ],
        }
        for field in domains:
            data = self.env['mrp.session'].read_group(
                domains[field] +
                [('shift_id', 'in', self.ids)],
                ['shift_id'], ['shift_id'])
            count = {
                x['shift_id'][0]: x['shift_id_count']
                for x in data if x['shift_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)

    name = fields.Char(
        string='Shift Name', required=True)
    code = fields.Char(
        string='Short Code', size=5, required=True,
        help="The shift sessions of will be named using this prefix.")
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        help='Person responsible for this shift')
    session_ids = fields.One2many(
        'mrp.session', 'shift_id', string='Sessions',
        help="Sessions created for this shift")
    resource_calendar_id = fields.Many2one(
        string="Work Schedule", help="Shift working schedule.")
    warehouse_id = fields.Many2one(
        'stock.warehouse', default=_default_warehouse_id)
    count_session = fields.Integer(compute='_compute_session_count')
    count_session_draft = fields.Integer(compute='_compute_session_count')
    count_session_confirmed = fields.Integer(compute='_compute_session_count')
    count_session_produced =  fields.Integer(compute='_compute_session_count')
    count_session_closed =  fields.Integer(compute='_compute_session_count')
    count_session_late = fields.Integer(compute='_compute_session_count')
    count_session_today = fields.Integer(compute='_compute_session_count')
