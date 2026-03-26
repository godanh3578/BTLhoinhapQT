from odoo import fields, models


class PheDuyetNghiepVu(models.Model):
    _name = 'phe_duyet_nghiep_vu'
    _description = 'Lịch sử phê duyệt nghiệp vụ'
    _order = 'ngay_duyet desc, id desc'

    de_nghi_mua_sam_id = fields.Many2one('de_nghi_mua_sam', string='Đề nghị mua sắm', required=True, ondelete='cascade')
    cap_duyet = fields.Selection([
        ('normal', 'Phê duyệt nghiệp vụ'),
        ('finance', 'Phê duyệt tài chính'),
        ('director', 'Phê duyệt lãnh đạo'),
    ], string='Cấp duyệt', default='normal', required=True)
    nguoi_duyet_id = fields.Many2one('res.users', string='Người duyệt', required=True, ondelete='restrict')
    ngay_duyet = fields.Datetime('Ngày duyệt', required=True, default=fields.Datetime.now)
    ket_qua = fields.Selection([
        ('submitted', 'Gửi duyệt'),
        ('reviewed', 'Đã kiểm tra'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ], string='Kết quả', required=True)
    y_kien = fields.Text('Ý kiến')
