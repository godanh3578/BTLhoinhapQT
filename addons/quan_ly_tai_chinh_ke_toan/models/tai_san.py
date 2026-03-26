from odoo import fields, models


class TaiSan(models.Model):
    _inherit = 'tai_san'

    de_nghi_mua_sam_id = fields.Many2one('de_nghi_mua_sam', string='Đề nghị mua sắm', ondelete='set null')
    chung_tu_mua_sam_id = fields.Many2one('chung_tu_mua_tai_san', string='Chứng từ mua sắm', ondelete='set null')
    ngay_ghi_tang = fields.Date('Ngày ghi tăng')
    gia_tri_thu_hoi_uoc_tinh = fields.Float('Giá trị thu hồi ước tính', default=0)
    dia_diem_su_dung = fields.Char('Địa điểm sử dụng')