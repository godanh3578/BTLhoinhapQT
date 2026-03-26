from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DeNghiMuaSam(models.Model):
    _name = 'de_nghi_mua_sam'
    _description = 'Đề nghị mua sắm tài sản'
    _rec_name = 'so_de_nghi'
    _order = 'ngay_de_nghi desc, id desc'

    so_de_nghi = fields.Char('Số đề nghị', required=True, copy=False, default='Mới')
    ngay_de_nghi = fields.Date('Ngày đề nghị', required=True, default=fields.Date.context_today)
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban đề nghị', required=True, ondelete='restrict')
    nguoi_de_nghi_id = fields.Many2one('nhan_vien', string='Người đề nghị', required=True, ondelete='restrict')
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', required=True, default=lambda self: self.env.company.currency_id)
    du_toan_chi_phi = fields.Monetary('Dự toán chi phí', currency_field='currency_id', compute='_compute_du_toan', store=True)
    ngan_sach_id = fields.Many2one('ngan_sach_mua_sam', string='Ngân sách', ondelete='restrict')
    nguon_kinh_phi_id = fields.Many2one('nguon_kinh_phi', string='Nguồn kinh phí', ondelete='restrict')
    noi_dung_mua_sam = fields.Text('Nội dung mua sắm')
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Chờ duyệt'),
        ('finance_review', 'Tài chính kiểm tra'),
        ('approved', 'Đã duyệt'),
        ('purchased', 'Đã mua'),
        ('done', 'Hoàn tất'),
        ('cancel', 'Hủy'),
    ], string='Trạng thái', default='draft', required=True)
    line_ids = fields.One2many('de_nghi_mua_sam_line', 'de_nghi_mua_sam_id', string='Hạng mục mua sắm')
    chung_tu_ids = fields.One2many('chung_tu_mua_tai_san', 'de_nghi_mua_sam_id', string='Chứng từ mua tài sản')
    phe_duyet_ids = fields.One2many('phe_duyet_nghiep_vu', 'de_nghi_mua_sam_id', string='Lịch sử phê duyệt')
    tai_san_ids = fields.One2many('tai_san', 'de_nghi_mua_sam_id', string='Tài sản hình thành')
    so_chung_tu = fields.Integer('Số chứng từ', compute='_compute_counts')
    so_tai_san = fields.Integer('Số tài sản', compute='_compute_counts')

    @api.depends('line_ids.thanh_tien_du_kien')
    def _compute_du_toan(self):
        for record in self:
            record.du_toan_chi_phi = sum(record.line_ids.mapped('thanh_tien_du_kien'))

    @api.depends('chung_tu_ids', 'tai_san_ids')
    def _compute_counts(self):
        for record in self:
            record.so_chung_tu = len(record.chung_tu_ids)
            record.so_tai_san = len(record.tai_san_ids)

    @api.constrains('ngan_sach_id', 'du_toan_chi_phi', 'trang_thai')
    def _check_budget_limit(self):
        active_states = {'submitted', 'finance_review', 'approved', 'purchased', 'done'}
        for record in self:
            if record.trang_thai in active_states and record.ngan_sach_id and record.ngan_sach_id.so_tien_con_lai < 0:
                raise ValidationError('Ngân sách đã bị âm sau khi ghi nhận đề nghị này.')

    @api.onchange('nguoi_de_nghi_id')
    def _onchange_nguoi_de_nghi_id(self):
        if self.nguoi_de_nghi_id and self.nguoi_de_nghi_id.phong_ban_hien_tai_id:
            self.phong_ban_id = self.nguoi_de_nghi_id.phong_ban_hien_tai_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('so_de_nghi', 'Mới') == 'Mới':
                vals['so_de_nghi'] = self.env['ir.sequence'].next_by_code('de_nghi_mua_sam') or 'DNMS-MOI'
        return super().create(vals_list)

    def _create_approval_log(self, result):
        for record in self:
            self.env['phe_duyet_nghiep_vu'].create({
                'de_nghi_mua_sam_id': record.id,
                'cap_duyet': 'normal',
                'nguoi_duyet_id': self.env.user.id,
                'ngay_duyet': fields.Datetime.now(),
                'ket_qua': result,
                'y_kien': f'Ghi nhận thao tác trạng thái: {dict(self._fields["trang_thai"].selection).get(record.trang_thai)}',
            })

    def action_submit(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError('Cần ít nhất một hạng mục mua sắm trước khi gửi duyệt.')
            record.trang_thai = 'submitted'
        self._create_approval_log('submitted')

    def action_finance_review(self):
        self.write({'trang_thai': 'finance_review'})
        self._create_approval_log('reviewed')

    def action_approve(self):
        self.write({'trang_thai': 'approved'})
        self._create_approval_log('approved')

    def action_mark_purchased(self):
        self.write({'trang_thai': 'purchased'})

    def action_done(self):
        self.write({'trang_thai': 'done'})

    def action_cancel(self):
        self.write({'trang_thai': 'cancel'})

    def action_reset_draft(self):
        self.write({'trang_thai': 'draft'})

    def action_view_chung_tu(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chứng từ mua tài sản',
            'res_model': 'chung_tu_mua_tai_san',
            'view_mode': 'kanban,tree,form',
            'domain': [('de_nghi_mua_sam_id', '=', self.id)],
            'context': {'default_de_nghi_mua_sam_id': self.id},
        }

    def action_view_tai_san(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tài sản hình thành',
            'res_model': 'tai_san',
            'view_mode': 'tree,form',
            'domain': [('de_nghi_mua_sam_id', '=', self.id)],
            'context': {'default_de_nghi_mua_sam_id': self.id},
        }


class DeNghiMuaSamLine(models.Model):
    _name = 'de_nghi_mua_sam_line'
    _description = 'Hạng mục đề nghị mua sắm'

    de_nghi_mua_sam_id = fields.Many2one('de_nghi_mua_sam', string='Đề nghị mua sắm', required=True, ondelete='cascade')
    ten_hang_muc = fields.Char('Tên hạng mục', required=True)
    so_luong = fields.Float('Số lượng', default=1, required=True)
    don_gia_du_kien = fields.Monetary('Đơn giá dự kiến', required=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='de_nghi_mua_sam_id.currency_id', store=True, readonly=True)
    thanh_tien_du_kien = fields.Monetary('Thành tiền dự kiến', compute='_compute_thanh_tien', store=True, currency_field='currency_id')
    co_hinh_thanh_tai_san = fields.Boolean('Hình thành tài sản', default=True)
    danh_muc_ts_id = fields.Many2one('danh_muc_tai_san', string='Loại tài sản', ondelete='restrict')
    mo_ta = fields.Char('Mô tả')

    @api.depends('so_luong', 'don_gia_du_kien')
    def _compute_thanh_tien(self):
        for record in self:
            record.thanh_tien_du_kien = record.so_luong * record.don_gia_du_kien

    @api.constrains('so_luong', 'don_gia_du_kien')
    def _check_positive_values(self):
        for record in self:
            if record.so_luong <= 0:
                raise ValidationError('Số lượng phải lớn hơn 0.')
            if record.don_gia_du_kien < 0:
                raise ValidationError('Đơn giá dự kiến không được âm.')