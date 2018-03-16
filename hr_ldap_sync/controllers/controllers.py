# -*- coding: utf-8 -*-
from odoo import http

# class Hr-ldap-sync(http.Controller):
#     @http.route('/hr-ldap-sync/hr-ldap-sync/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr-ldap-sync/hr-ldap-sync/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr-ldap-sync.listing', {
#             'root': '/hr-ldap-sync/hr-ldap-sync',
#             'objects': http.request.env['hr-ldap-sync.hr-ldap-sync'].search([]),
#         })

#     @http.route('/hr-ldap-sync/hr-ldap-sync/objects/<model("hr-ldap-sync.hr-ldap-sync"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr-ldap-sync.object', {
#             'object': obj
#         })