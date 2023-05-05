# -*- coding: utf-8 -*-
# from odoo import http


# class SimplePurchase(http.Controller):
#     @http.route('/simple_purchase/simple_purchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/simple_purchase/simple_purchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('simple_purchase.listing', {
#             'root': '/simple_purchase/simple_purchase',
#             'objects': http.request.env['simple_purchase.simple_purchase'].search([]),
#         })

#     @http.route('/simple_purchase/simple_purchase/objects/<model("simple_purchase.simple_purchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('simple_purchase.object', {
#             'object': obj
#         })
