from odoo import models, fields, api


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'
    _rec_name = 'ten_chuc_vu'
    _sql_constraints = [
        ('ma_chuc_vu_unique', 'unique(ma_chuc_vu)', 'Mã chức vụ đã tồn tại.'),
    ]

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)  
    vai_tro_he_thong = fields.Selection([
        ('employee', 'Nhân viên'),
        ('accountant', 'Kế toán'),
        ('manager', 'Quản lý'),
        ('director', 'Giám đốc'),
    ], string='Vai trò hệ thống', default='employee', required=True)
    duoc_tao_giao_dich_tai_chinh = fields.Boolean('Được tạo giao dịch tài chính')
    duoc_phe_duyet_tai_chinh = fields.Boolean('Được phê duyệt giao dịch tài chính')
    duoc_ghi_so_ke_toan = fields.Boolean('Được ghi sổ kế toán')
    han_muc_phe_duyet_tai_chinh = fields.Float('Hạn mức phê duyệt tài chính', help='Để 0 nếu không giới hạn.')
    lich_su_cong_tac_ids = fields.One2many("lich_su_cong_tac",string="Danh sách lịch sử công tác", inverse_name="chuc_vu_id")

    @api.onchange('vai_tro_he_thong')
    def _onchange_vai_tro_he_thong(self):
        role_map = {
            'employee': {'duoc_tao_giao_dich_tai_chinh': True, 'duoc_phe_duyet_tai_chinh': False, 'duoc_ghi_so_ke_toan': False},
            'accountant': {'duoc_tao_giao_dich_tai_chinh': True, 'duoc_phe_duyet_tai_chinh': False, 'duoc_ghi_so_ke_toan': True},
            'manager': {'duoc_tao_giao_dich_tai_chinh': True, 'duoc_phe_duyet_tai_chinh': True, 'duoc_ghi_so_ke_toan': False},
            'director': {'duoc_tao_giao_dich_tai_chinh': True, 'duoc_phe_duyet_tai_chinh': True, 'duoc_ghi_so_ke_toan': False},
        }
        values = role_map.get(self.vai_tro_he_thong, {})
        for field_name, value in values.items():
            setattr(self, field_name, value)
        if self.vai_tro_he_thong == 'director' and not self.han_muc_phe_duyet_tai_chinh:
            self.han_muc_phe_duyet_tai_chinh = 0
   