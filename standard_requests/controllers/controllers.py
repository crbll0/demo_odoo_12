# -*- coding: utf-8 -*-
from odoo import http

# class StandardRequests(http.Controller):
#     @http.route('/standard_requests/standard_requests/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/standard_requests/standard_requests/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('standard_requests.listing', {
#             'root': '/standard_requests/standard_requests',
#             'objects': http.request.env['standard_requests.standard_requests'].search([]),
#         })

#     @http.route('/standard_requests/standard_requests/objects/<model("standard_requests.standard_requests"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('standard_requests.object', {
#             'object': obj
#         })