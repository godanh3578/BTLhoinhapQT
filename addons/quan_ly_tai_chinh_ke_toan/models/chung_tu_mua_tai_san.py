from odoo import api, fields, models


class ChungTuMuaTaiSan(models.Model):
    _name = 'chung_tu_mua_tai_san'
    _description = 'Chứng từ mua tài sản'
    _rec_name = 'so_chung_tu'
    _order = 'ngay_chung_tu desc, id desc'

    so_chung_tu = fields.Char('Số chứng từ', required=True, copy=False, default='Mới')
    ngay_chung_tu = fields.Date('Ngày chứng từ', required=True, default=fields.Date.context_today)
    doi_tac = fields.Char('Đối tác / Nhà cung cấp', required=True)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', required=True, default=lambda self: self.env.company.currency_id)
    gia_tri_thanh_toan = fields.Monetary('Giá trị thanh toán', currency_field='currency_id', required=True)
    de_nghi_mua_sam_id = fields.Many2one('de_nghi_mua_sam', string='Đề nghị mua sắm', required=True, ondelete='restrict')
    account_move_id = fields.Many2one('account.move', string='Bút toán kế toán', ondelete='set null')
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('posted', 'Đã ghi nhận'),
        ('cancel', 'Hủy'),
    ], string='Trạng thái', default='draft', required=True)
    ghi_chu = fields.Text('Ghi chú')
    tai_san_ids = fields.One2many('tai_san', 'chung_tu_mua_sam_id', string='Tài sản liên kết')
    so_tai_san = fields.Integer('Số tài sản', compute='_compute_so_tai_san')

    def _compute_so_tai_san(self):
        for record in self:
            record.so_tai_san = len(record.tai_san_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('so_chung_tu', 'Mới') == 'Mới':
                vals['so_chung_tu'] = self.env['ir.sequence'].next_by_code('chung_tu_mua_tai_san') or 'CTTS-MOI'
        return super().create(vals_list)

    def action_mark_posted(self):
        self.write({'trang_thai': 'posted'})
        self.mapped('de_nghi_mua_sam_id').write({'trang_thai': 'purchased'})

    def action_cancel(self):
        self.write({'trang_thai': 'cancel'})

    def action_view_tai_san(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tài sản liên kết',
            'res_model': 'tai_san',
            'view_mode': 'tree,form',
            'domain': [('chung_tu_mua_sam_id', '=', self.id)],
            'context': {'default_chung_tu_mua_sam_id': self.id, 'default_de_nghi_mua_sam_id': self.de_nghi_mua_sam_id.id},
        }