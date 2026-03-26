from odoo import api, fields, models


class NguonKinhPhi(models.Model):
    _name = 'nguon_kinh_phi'
    _description = 'Nguồn kinh phí mua sắm'
    _rec_name = 'ten_nguon'
    _order = 'ma_nguon desc'

    ma_nguon = fields.Char('Mã nguồn', required=True, copy=False, default='Mới')
    ten_nguon = fields.Char('Tên nguồn', required=True)
    loai_nguon = fields.Selection([
        ('company', 'Ngân sách công ty'),
        ('project', 'Ngân sách dự án'),
        ('department', 'Ngân sách phòng ban'),
        ('other', 'Khác'),
    ], string='Loại nguồn', default='company', required=True)
    ghi_chu = fields.Text('Ghi chú')
    trang_thai = fields.Selection([
        ('active', 'Đang sử dụng'),
        ('inactive', 'Ngừng sử dụng'),
    ], string='Trạng thái', default='active', required=True)
    de_nghi_mua_sam_ids = fields.One2many('de_nghi_mua_sam', 'nguon_kinh_phi_id', string='Đề nghị mua sắm')
    so_de_nghi = fields.Integer('Số đề nghị', compute='_compute_so_de_nghi')

    @api.depends('de_nghi_mua_sam_ids')
    def _compute_so_de_nghi(self):
        for record in self:
            record.so_de_nghi = len(record.de_nghi_mua_sam_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ma_nguon', 'Mới') == 'Mới':
                vals['ma_nguon'] = self.env['ir.sequence'].next_by_code('nguon_kinh_phi') or 'NKP-MOI'
        return super().create(vals_list)

    def action_view_de_nghi(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đề nghị mua sắm',
            'res_model': 'de_nghi_mua_sam',
            'view_mode': 'kanban,tree,form',
            'domain': [('nguon_kinh_phi_id', '=', self.id)],
            'context': {'default_nguon_kinh_phi_id': self.id},
        }