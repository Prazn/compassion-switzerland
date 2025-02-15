##############################################################################
#
#    Copyright (C) 2017 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import fields, models


class CompassionProject(models.Model):
    _inherit = "compassion.project"

    description_fr = fields.Html("French description", readonly=True)
    description_de = fields.Html("German description", readonly=True)
    description_it = fields.Html("Italian description", readonly=True)
    description = fields.Html(compute="_compute_description")
    description_left = fields.Html(compute="_compute_description")
    description_right = fields.Html(compute="_compute_description")

    def _compute_description(self):
        lang_map = {
            "fr_CH": "description_fr",
            "de_DE": "description_de",
            "en_US": "description_en",
            "it_IT": "description_it",
        }

        for project in self:
            lang = self.env.lang or "en_US"
            description = getattr(project, lang_map.get(lang), "")
            project.description_right = description
            project.description_left = ""
            project.description = description
