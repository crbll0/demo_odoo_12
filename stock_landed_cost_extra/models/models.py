# -*- coding: utf-8 -*-

import logging
from collections import defaultdict, Counter

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    
    no_cost_lines = fields.One2many('stock.landed.cost.lines.remove', 'cost_id')
    
    @api.multi
    def compute_landed_cost(self):
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()
        
        NoCost = self.env['stock.landed.cost.lines.remove']
        
        cost_totals_type = {}
        digits = dp.get_precision('Product Price')(self._cr)
        towrite_dict = {}
        for cost in self.filtered(lambda cost: cost.picking_ids):

            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    totals = {
                        'total_qty': 0.0,
                        'total_cost': 0.0,
                        'total_weight': 0.0,
                        'total_volume': 0.0,
                        'total_line': 0.0,
                    }
                    
                    no_cost = NoCost.search([
                        ('cost_line_id', '=', cost_line.id),
                        ('product_id', '=', val_line_values.get('product_id'))
                    ])
                    
                    if no_cost: continue
                    
                    totals.update({
                        'total_qty': val_line_values.get('quantity', 0.0),
                        'total_cost': val_line_values.get('former_cost', 0.0),
                        'total_weight': val_line_values.get('weight', 0.0),
                        'total_volume': val_line_values.get('volume', 0.0),
                        'total_line': 1,
                    })
                    
                    temp = Counter(totals)
                    if cost_line.id not in cost_totals_type:
                        cost_totals_type[cost_line.id] = temp
                        
                    else:
                        cost_totals_type[cost_line.id] += temp
                        
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
               
                #former_cost = val_line_values.get('former_cost', 0.0)
                # round this because former_cost on the valuation lines is also rounded
                #total_cost += tools.float_round(former_cost, precision_digits=digits[1]) if digits else former_cost

                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                   
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        cost_totals = cost_totals_type[line.id]
                        
                        if line.split_method == 'by_quantity' and cost_totals.get('total_qty'):
                            per_unit = (line.price_unit / cost_totals.get('total_qty'))
                            value = valuation.quantity * per_unit
                            
                        elif line.split_method == 'by_weight' and cost_totals.get('total_weight'):
                            per_unit = (line.price_unit / cost_totals.get('total_weight'))
                            value = valuation.weight * per_unit
                            
                        elif line.split_method == 'by_volume' and cost_totals.get('total_volume'):
                            per_unit = (line.price_unit / cost_totals.get('total_volume'))
                            value = valuation.volume * per_unit
                            
                        elif line.split_method == 'equal':
                            value = (line.price_unit / cost_totals.get('total_line'))
                            
                        elif line.split_method == 'by_current_cost_price' and cost_totals.get('total_cost'):
                            per_unit = (line.price_unit / cost_totals.get('total_cost'))
                            value = valuation.former_cost * per_unit
                            
                        else:
                            value = (line.price_unit / total_line)
                       
                        if digits:
                            value = tools.float_round(value, precision_digits=digits[1], rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value
                        
                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
                            
        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        return True


class LandedCostLinesRemove(models.Model):
    _name = 'stock.landed.cost.lines.remove'
    _description = 'Stock Landed Cost Lines Remove'
    
    cost_id = fields.Many2one('stock.landed.cost', string='Landed Cost')
    cost_line_id = fields.Many2one('stock.landed.cost.lines', string='Costo')
    product_id = fields.Many2one('product.product', string='Producto')
