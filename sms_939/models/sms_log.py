##############################################################################
#
#    Copyright (C) 2019 Compassion CH (http://www.compassion.ch)
#    @author: Théo Nikles <theo.nikles@gmail.com>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import fields, models


class LogSMS(models.Model):
    _name = "sms.log"
    _description = "Log of SMS"

    partner_id = fields.Many2one("res.partner", "Partner", readonly=False)
    text = fields.Text(required=True)
    subject = fields.Char()
    date = fields.Datetime(default=fields.Datetime.now)
