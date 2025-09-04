# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    tax_rounding_method = fields.Selection(
        selection=[("HALF-UP", "Half-up"), ("UP", "Round-up"), ("DOWN", "Round-down")],
        default="HALF-UP",
    )
