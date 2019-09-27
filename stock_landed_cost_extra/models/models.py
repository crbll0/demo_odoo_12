# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    
    no_cost_lines = fields.One2many('stock.landed.cost.lines.remove', 'cost_id')
    

class LandedCostLinesRemove(models.Model):
    _name = 'stock.landed.cost.lines.remove'
    
    cost_id = fields.Many2one('stock.landed.cost', 'Landed Cost')
    
    cost_line_id = fields.Many2one('stock.landed.cost.lines', 'Costo')
    product_id = fields.Many2one('product.product', 'Producto')
