from openerp import models, api
from openerp.exceptions import ValidationError
from openerp.tools.safe_eval import safe_eval


class IrCron(models.Model):
    _inherit = "ir.cron"

    @api.multi
    def action_manual_exec(self):
        for rec in self:
            model_obj = self.env[rec.model]
            args = self.str2tuple(rec.args)

            function_obj = getattr(model_obj, rec.function)
            if not function_obj:
                raise ValidationError("Method not found")

            function_obj(*args)

    @staticmethod
    def str2tuple(s):
        return safe_eval('tuple(%s)' % (s or ''))
