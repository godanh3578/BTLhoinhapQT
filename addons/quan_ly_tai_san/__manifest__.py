# -*- coding: utf-8 -*-
{
    'name': 'Quản lý tài sản',
    'summary': 'Quản lý tài sản, phân bổ sử dụng và khấu hao hàng tháng vào sổ cái',
    'description': 'Quản lý tài sản doanh nghiệp, phân bổ cho nhân sự và tự động ghi nhận khấu hao vào kế toán.',
    'author': 'BTL hội nhập QT',
    'website': 'http://www.yourcompany.com',
    'category': 'Accounting',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'application': True,
    'depends': ['base', 'account', 'nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'data/asset_cron.xml',
        'views/danh_muc_tai_san.xml',
        'views/phan_bo_tai_san.xml',
        'views/tai_san.xml',
        'views/lich_su_khau_hao.xml',
        'views/menu.xml',
    ],
    'demo': [],
}