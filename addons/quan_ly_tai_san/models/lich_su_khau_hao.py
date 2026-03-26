from odoo import api, fields, models
from odoo.exceptions import ValidationError

class LichSuKhauHao(models.Model):
    _name = 'lich_su_khau_hao'
    _description = 'lich_su_khau_hao'
    _rec_name = "ma_phieu_khau_hao"
    _order = 'ngay_khau_hao desc'
    _sql_constraints = [
        ("ma_phieu_khau_hao_unique", "unique(ma_phieu_khau_hao)", "Mã phiếu khấu hao đã tồn tại !"),
        ('asset_period_unique', 'unique(ma_ts, ky_khau_hao)', 'Tài sản đã có khấu hao cho kỳ này.'),
    ]
    
    ma_phieu_khau_hao = fields.Char('Mã phiếu', default='KHTS-', required=True)
    ma_ts = fields.Many2one('tai_san', string='Mã tài sản', required=True, ondelete='cascade')
    ngay_khau_hao = fields.Datetime('Ngày khấu hao',default = fields.Datetime.now(),  required=True)
    ky_khau_hao = fields.Char('Kỳ khấu hao', required=True)
    gia_tri_truoc_khau_hao = fields.Float('Giá trị trước khấu hao', required=True)
    so_tien_khau_hao = fields.Float('Số tiền khấu hao', required=True, default=0)
    gia_tri_con_lai = fields.Float(string='Giá trị còn lại', store=True)
    but_toan_id = fields.Many2one('account.move', string='Bút toán kế toán', readonly=True, ondelete='set null')
    
    loai_phieu = fields.Selection([
        ('automatic', 'Tự động'),
        ('manual', 'Thủ công')
    ], string='Phương thức', required=True)
    ghi_chu = fields.Char('Ghi chú')
    
    @api.model
    def create(self, vals):
        tai_san = self.env['tai_san'].browse(vals.get('ma_ts'))
        if tai_san:
            so_tien_khau_hao = vals.get('so_tien_khau_hao', 0)
            if tai_san.gia_tri_hien_tai == 0:
                raise ValidationError("Tài sản đã hết giá trị, không thể khấu hao !")
            if so_tien_khau_hao > tai_san.gia_tri_hien_tai:
                so_tien_khau_hao = tai_san.gia_tri_hien_tai
            vals.setdefault('gia_tri_truoc_khau_hao', tai_san.gia_tri_hien_tai)
            vals['gia_tri_con_lai'] = max(0, tai_san.gia_tri_hien_tai - so_tien_khau_hao)
            tai_san.gia_tri_hien_tai = vals['gia_tri_con_lai']
            tai_san.so_thang_da_khau_hao += tai_san.chu_ky_khau_hao_thang
        return super().create(vals)    
