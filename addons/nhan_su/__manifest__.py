# -*- coding: utf-8 -*-
{
    'name': 'Quản lý nhân sự',
    'summary': 'Quản lý hồ sơ nhân viên, phòng ban, chức vụ và lịch sử công tác',
    'description': 'Module dữ liệu gốc nhân sự cho các phần hệ thống liên quan.',
    'author': 'BTL hội nhập QT',
    'website': 'http://www.yourcompany.com',
    'category': 'Human Resources',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'application': True,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/nhan_vien.xml',
        'views/phong_ban.xml',
        'views/chuc_vu.xml',
        'views/lich_su_cong_tac.xml',
        'views/menu.xml',
    ],
    'demo': [],
}
