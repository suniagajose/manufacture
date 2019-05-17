# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class MrpWorkline(models.Model):
    """Added Manufacture Workline."""

    _name = 'mrp.workline'
    _description = "Manufacture Workline"

    name = fields.Char(
        string='Workline Name', required=True)
    code = fields.Char(
        string='Workline Code', size=5, required=True,
        help="The shift sessions of will be named using this prefix.")

