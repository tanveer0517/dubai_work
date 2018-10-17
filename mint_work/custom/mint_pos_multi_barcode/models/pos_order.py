# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class ProductMultiBarcode(models.Model):
    _name = 'product.multi.barcode'

    _rec_name = 'parent_barcode'

    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Many2one('stock.production.lot', string='LOT/Serial')
    parent_barcode = fields.Char('Parent Barcode')
    child_barcode = fields.Char('Child Barcode')
    qty = fields.Float('Qty')
    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure',)

    _sql_constraints = [('lot_id_uniq', 'unique (lot_id)', 'Lot Should be Unique for multiple barcode.'),
                        ('parent_barcode_uniq', 'unique (parent_barcode)', 'Parent Barcode Should be Unique for multiple barcode.'),
                        ('child_barcode_uniq', 'unique (child_barcode)', 'Child Barcode Should be Unique for multiple barcode.')]
    #On change lot id get the lot id related information and set it on its related fields.
    @api.onchange('lot_id')
    def on_change_lot_id(self):
        for rec in self:
            if rec.lot_id:
                rec.parent_barcode = rec.lot_id.barcode or False
                rec.child_barcode = rec.lot_id.child_barcode or False
                rec.qty = rec.lot_id.product_qty or 0
                rec.product_id = rec.lot_id.product_id and rec.lot_id.product_id.id or False
                rec.product_uom_id = rec.lot_id.product_uom_id and rec.lot_id.product_uom_id.id or False


class ProductProductMultiBarcode(models.Model):
    _inherit = 'product.product'

    #One2many field to add multi barcode on product.
    multi_barcode_ids = fields.One2many('product.multi.barcode', 'product_id', string="Multi Barcode")

class Picking(models.Model):
    _inherit = "stock.picking"

    #inherit this method to pss the childbarcode and uom information.
    def _create_lots_for_picking(self):
        Lot = self.env['stock.production.lot']
        for pack_op_lot in self.mapped('pack_operation_ids').mapped('pack_lot_ids'):
            if not pack_op_lot.lot_id:
                lot = Lot.create({'name': pack_op_lot.lot_name,
                                  'child_barcode': pack_op_lot.child_barcode,
                                  'product_id': pack_op_lot.operation_id.product_id.id,
                                  'product_qty': pack_op_lot.qty,
                                  'product_uom_id': pack_op_lot.operation_id.product_uom_id.id,})
                pack_op_lot.write({'lot_id': lot.id})
        # TDE FIXME: this should not be done here
        self.mapped('pack_operation_ids').mapped('pack_lot_ids').filtered(lambda op_lot: op_lot.qty == 0.0).unlink()
    create_lots_for_picking = _create_lots_for_picking


class PackOperationLotBarcode(models.Model):
    _inherit = "stock.pack.operation.lot"

    child_barcode = fields.Char(
        'Child Barcode', copy=False,
        help="International Article Number used for lot identification.")

class StockProductionLotBarcode(models.Model):
    _inherit = 'stock.production.lot'

    child_barcode = fields.Char(
        'Child Barcode', copy=False,
        help="International Article Number used for lot identification.")

    #override create method to  create a new multi barcode record related to product lot.
    @api.model
    def create(self, vals):
        lot_id = super(StockProductionLotBarcode, self).create(vals)
        if lot_id:
            self.env['product.multi.barcode'].create({
                'lot_id': lot_id.id,
                'product_id': lot_id.product_id.id,
                'parent_barcode': lot_id.barcode,
                'child_barcode': lot_id.child_barcode,
                'qty': vals.get('product_qty',0),
                'product_uom_id': vals.get('product_uom_id',False),
            })
        return lot_id
