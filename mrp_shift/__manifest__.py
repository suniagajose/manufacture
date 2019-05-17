# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Working Shift Management",
    "version": "12.0.1.0.0",
    "author": "Vauxoo, Odoo Community Association (OCA)",
    "website": "https://github.com/oca/mrp",
    "license": "AGPL-3",
    "category": "Manufacture",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_session_view.xml",
        "views/mrp_shift_view.xml",
        "views/mrp_shift_template.xml",
    ],
    'installable': True
}
