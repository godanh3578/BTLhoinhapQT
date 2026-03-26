# -*- coding: utf-8 -*-
{
    'name': 'Quản lý tài chính kế toán',
    'summary': 'Ngân sách mua sắm, nguồn kinh phí, chứng từ và liên kết tài sản doanh nghiệp',
    'description': 'Quản lý đề nghị mua sắm, ngân sách, nguồn kinh phí, chứng từ mua tài sản và liên kết với kế toán, tài sản.',
    'author': 'BTL hội nhập QT',
    'website': 'http://www.yourcompany.com',
    'category': 'Accounting',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'application': True,
    'depends': ['base', 'account', 'nhan_su', 'quan_ly_tai_san'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/finance_integration_settings_views.xml',
        'views/ngan_sach_mua_sam_views.xml',
        'views/nguon_kinh_phi_views.xml',
        'views/de_nghi_mua_sam_views.xml',
        'views/chung_tu_mua_tai_san_views.xml',
        'views/phe_duyet_nghiep_vu_views.xml',
        'views/tai_san_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'quan_ly_tai_chinh_ke_toan/static/src/scss/finance_backend.scss',
        ],
    },
}