##############################################################################
#
#    Copyright (C) 2016 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from datetime import date

from odoo import api, fields, models


class AccountInvoice(models.Model):
    """
    Make Invoice translatable for communications with dates.
    """

    _inherit = ["account.move", "translatable.model"]
    _name = "account.move"

    # Gender field is mandatory for translatable models
    gender = fields.Char(compute="_compute_gender")

    def _compute_gender(self):
        for i in self:
            i.gender = "M"


class Contract(models.Model):
    _inherit = "recurring.contract"

    amount_due = fields.Integer(compute="_compute_amount_due", store=True)

    def _compute_amount_due(self):
        this_month = date.today().replace(day=1)
        for contract in self:
            if (
                contract.child_id.project_id.suspension != "fund-suspended"
                and contract.type not in ["SC", "SWP"]
            ):
                invoice_lines = contract.invoice_line_ids.with_context(
                    lang="en_US"
                ).filtered(
                    lambda i: i.payment_state == "not_paid"
                    and i.due_date < this_month
                    and i.move_id.invoice_category == "sponsorship"
                )
                contract.amount_due = int(sum(invoice_lines.mapped("price_subtotal")))

    def get_gift_communication(self, product):
        self.ensure_one()
        lang = self.mapped(self.send_gifts_to).lang
        child = self.child_id.with_context(lang=lang)
        born = {
            "en_US": "Born in",
            "fr_CH": "Né le" if child.gender == "M" else "Née le",
            "de_DE": "Geburtstag",
            "it_IT": "Compleanno",
        }
        birthdate = child.birthdate.strftime("%d.%m.%Y")
        vals = {
            "firstname": child.preferred_name,
            "local_id": child.local_id,
            "product": product.with_context(lang=lang).name,
            "birthdate": born[lang] + " " + birthdate
            if "Birthday" in product.with_context(lang="en_US").name
            else "",
        }
        if "Birthday" in product.with_context(lang="en_US").name:
            communication = (
                f"{vals['firstname']} ({vals['local_id']})"
                f"<br/>{vals['product']}"
                f"<br/>{vals['birthdate']}"
            )
        else:
            communication = (
                f"{vals['firstname']} ({vals['local_id']})" f"<br/>{vals['product']}"
            )
        gift_threshold = self.env["gift.threshold.settings"].search(
            [("product_id", "=", product.id)], limit=1
        )
        if gift_threshold:
            min_amount = int(gift_threshold.min_amount)
            max_amount = int(gift_threshold.max_amount)
            amount_limit = {
                "en_US": f"CHF {min_amount}.- to max {max_amount}.- per year",
                "fr_CH": f"CHF {min_amount}.- à max. {max_amount}.- par année",
                "de_DE": f"CHF {min_amount}.- bis max. {max_amount}.- pro Jahr",
                "it_IT": f"Importo tra CHF {min_amount}.- e {max_amount}.- per anno",
            }
            communication += f"<br/>{amount_limit[lang]}"
        return communication

    @api.model
    def get_sponsorship_gift_products(self):
        gift_categ_id = self.env.ref("sponsorship_compassion.product_category_gift").id
        return self.env["product.product"].search([("categ_id", "=", gift_categ_id)])
