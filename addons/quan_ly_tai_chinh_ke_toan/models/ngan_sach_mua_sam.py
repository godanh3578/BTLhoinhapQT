from odoo import api, fields, models


class NganSachMuaSam(models.Model):
    _name = 'ngan_sach_mua_sam'
    _description = 'Ngân sách mua sắm tài sản'
    _rec_name = 'ten_ngan_sach'
    _order = 'nam_ngan_sach desc, ma_ngan_sach desc'

    ma_ngan_sach = fields.Char('Mã ngân sách', required=True, copy=False, default='Mới')
    ten_ngan_sach = fields.Char('Tên ngân sách', required=True)
    nam_ngan_sach = fields.Integer('Năm ngân sách', required=True, default=lambda self: fields.Date.today().year)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', required=True, default=lambda self: self.env.company.currency_id)
    so_tien_duyet = fields.Monetary('Số tiền duyệt', currency_field='currency_id', required=True)
    so_tien_da_dung = fields.Monetary('Số tiền đã dùng', currency_field='currency_id', compute='_compute_amounts', store=True)
    so_tien_con_lai = fields.Monetary('Số tiền còn lại', currency_field='currency_id', compute='_compute_amounts', store=True)
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('open', 'Đang sử dụng'),
        ('closed', 'Đã khóa'),
    ], string='Trạng thái', default='draft', required=True)
    mo_ta = fields.Text('Mô tả')
    de_nghi_mua_sam_ids = fields.One2many('de_nghi_mua_sam', 'ngan_sach_id', string='Đề nghị mua sắm')
    so_de_nghi = fields.Integer('Số đề nghị', compute='_compute_so_de_nghi')

    @api.depends('de_nghi_mua_sam_ids.du_toan_chi_phi', 'de_nghi_mua_sam_ids.trang_thai')
    def _compute_amounts(self):
        valid_states = {'finance_review', 'approved', 'purchased', 'done'}
        for record in self:
            used_amount = sum(record.de_nghi_mua_sam_ids.filtered(lambda item: item.trang_thai in valid_states).mapped('du_toan_chi_phi'))
            record.so_tien_da_dung = used_amount
            record.so_tien_con_lai = record.so_tien_duyet - used_amount

    @api.depends('de_nghi_mua_sam_ids')
    def _compute_so_de_nghi(self):
        for record in self:
            record.so_de_nghi = len(record.de_nghi_mua_sam_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ma_ngan_sach', 'Mới') == 'Mới':
                vals['ma_ngan_sach'] = self.env['ir.sequence'].next_by_code('ngan_sach_mua_sam') or 'NSMS-MOI'
        return super().create(vals_list)

    def action_open(self):
        self.write({'trang_thai': 'open'})

    def action_close(self):
        self.write({'trang_thai': 'closed'})

    def action_view_de_nghi(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đề nghị mua sắm',
            'res_model': 'de_nghi_mua_sam',
            'view_mode': 'kanban,tree,form',
            'domain': [('ngan_sach_id', '=', self.id)],
            'context': {'default_ngan_sach_id': self.id},
        }