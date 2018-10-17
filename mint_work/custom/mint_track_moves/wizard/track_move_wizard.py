# -*- coding: utf-8 -*-
import math


from odoo import _, api, models, fields
from odoo.exceptions import Warning


class TrackStockQuant(models.TransientModel):
    _name = 'track.stock.quant'

    search_type = fields.Selection([('barcode', 'Barcode'),
                                       ('lot', 'Lot/serial')],
                                      string = 'Search By',
                                      default = 'barcode')
    product_barcode = fields.Char('Barcode', help="""Enter Product Barcode 
    Manually or Scan through the barcode machine.""")
    lot_serial_no = fields.Char('Lot/Serial Number', help="""Enter the Lot 
    Number or the Serial Number to get related data from Moves""")
    operation_type = fields.Selection([('incoming', 'Vendor'),
                                       ('outgoing', 'Customer'),
                                       ('internal', 'Internal')],
                                      string='Operation Type',
                                      default='outgoing')


    # This method will get all the tracked moves by barcode, or child
    # barcode if there in product, or by lot from the wizard
    @api.multi
    def get_tracked_moves(self):
        op_type = self.operation_type
        stock_product_lot_obj = self.env['stock.production.lot']
        if self.search_type == 'barcode':
            barcode = self.product_barcode
            if barcode:
                if 'child_barcode' in stock_product_lot_obj._fields:
                    query = """
                        select sm.id, sm.product_id from stock_move sm
                        left join stock_quant_move_rel sqmr on sm.id = sqmr.move_id
                        left join stock_picking_type spt on sm.picking_type_id = spt.id
                        left join stock_quant sq on sq.id = sqmr.quant_id
                        left join stock_production_lot spl on spl.id = sq.lot_id
                        left join product_multi_barcode pmb on pmb.product_id = sm.product_id
                        where spt.code = '%s' and pmb.child_barcode = '%s';""" % (op_type, barcode)
                    self.env.cr.execute(query)
                    result = self._cr.fetchall()
                    result = [each[0] for each in result if each]
                else:
                    query = """
                        select sm.id, sm.product_id from stock_move sm
                        left join stock_quant_move_rel sqmr on sm.id = sqmr.move_id
                        left join stock_picking_type spt on sm.picking_type_id = spt.id
                        left join stock_quant sq on sq.id = sqmr.quant_id
                        left join stock_production_lot spl on spl.id = sq.lot_id
                        left join product_product pp on pp.id = sm.product_id
                        where spt.code = '%s' and pp.barcode = '%s';""" % (op_type, barcode)
                    self.env.cr.execute(query)
                    result = self._cr.fetchall()
                    result = [each[0] for each in result if each]
                if not result:
                    raise Warning(_("No Stock Move Found related to this "
                                "barcode"))
            else:
                raise Warning(_("Please enter Barcode"))

        if self.search_type == 'lot':
            lot_serial_no = self.lot_serial_no
            if lot_serial_no:
                query = """
                    select sm.id from stock_move sm
                    left join stock_quant_move_rel sqmr on sm.id = sqmr.move_id
                    left join stock_picking_type spt on sm.picking_type_id = spt.id
                    left join stock_quant sq on sq.id = sqmr.quant_id
                    left join stock_production_lot spl on spl.id = sq.lot_id
                    where spt.code ='%s' and spl.name ='%s';
                    """ % (op_type, lot_serial_no)
                self.env.cr.execute(query)
                result = self._cr.fetchall()
                result = [each[0] for each in result if each]
                if not result:
                    raise Warning(_("No Stock Move found related to this "
                                "Lot/Serial No provided"))
            else:
                raise Warning(_("Please enter lot no or serial no"))

        res =  {
            'domain': [('id','in',result)],
            'name' : _('My Tracked Moves'),
            'type': 'ir.actions.act_window',
            'view_type' : 'form',
            'view_mode' : 'tree,form',
            'res_model': 'stock.move',
            'no_destroy': True,
            'context': {'tree_view_ref': 'stock.view_move_tree',
                        'form_view_ref': 'stock.view_move_form'}
            }
        return res
