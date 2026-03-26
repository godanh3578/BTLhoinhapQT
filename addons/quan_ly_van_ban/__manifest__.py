# -*- coding: utf-8 -*-
{
    'name': 'Quản lý văn bản',
    'summary': 'Quản lý văn bản đến và liên kết với nhân sự xử lý, ký, nhận',
    'description': 'Quản lý văn bản đến và liên kết trực tiếp với hồ sơ nhân sự.',
    'author': 'BTL hội nhập QT',
    'website': 'http://www.yourcompany.com',
    'category': 'Human Resources',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'application': True,
    'depends': ['base', 'nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/van_ban_den.xml',
        'views/nhan_vien_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
}
