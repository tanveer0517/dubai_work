# -*- coding: utf-8 -*-
from odoo import models, fields, api


class addtocatalog(models.TransientModel):
    _name = 'add.to.catalog.wizard'

    @api.multi
    def add_to_catalog(self):
        if self._context and self._context.get('active_ids'):
            for pro in self._context.get('active_ids'):
                catalog_rec = self.env['product.catelog'].browse(pro)
                catalog_rec.update_template()
                product_rec = self.env['product.template'].browse(pro)
                try:
                    product_rec.gomartcatelog(company_id=self.env.user.company_id.id)
                except:
                    pass
    # csv_file = fields.Binary(string='CSV File', required=True)
    #
    # @api.multi
    # def import_csv(self):
    #     # this will get executed when you click the import button in your form
    #     return {}

    # @api.multi
    # def add_to_catalog(self):
    #     if self._context and self._context.get('active_ids'):
    #         for pro in self._context.get('active_ids'):
    #             catalog_rec = self.env['product.catelog'].browse(pro)
    #             catalog_rec.update_template()

