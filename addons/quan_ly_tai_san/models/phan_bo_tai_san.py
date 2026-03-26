from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PhanBoTaiSan(models.Model):
    _name = 'phan_bo_tai_san'
    _description = 'Bảng chứa thông tin Phân bổ tài sản'
    _rec_name = "tai_san_id"

    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban', required=True, ondelete='restrict')
    tai_san_id = fields.Many2one('tai_san', string='Tài sản', required=True, ondelete='cascade')
    ngay_phat = fields.Date('Ngày phân bổ', required=True, default=fields.Date.today())
    nhan_vien_su_dung_id = fields.Many2one(comodel_name = 'nhan_vien', string='Nhân viên sử dụng', ondelete='restrict')
    
    ghi_chu = fields.Char('Ghi chú', default='')
    trang_thai = fields.Selection([
        ('in-use', 'Đang sử dụng'),
        ('not-in-use', 'Không sử dụng')
    ], string='Trạng thái', required=True, default='in-use')
    vi_tri_tai_san_id = fields.Many2one('phong_ban', string='Vị trí tài sản', required=True, ondelete='restrict')
    ngay_thu_hoi = fields.Date('Ngày thu hồi')
    nguon_cap_nhat = fields.Selection([
        ('manual', 'Thủ công'),
        ('auto_reallocation', 'Tự động cấp phát lại'),
        ('auto_hr_transfer', 'Tự động do điều chuyển HR'),
    ], string='Nguồn cập nhật', default='manual', readonly=True, required=True)

    custom_name = fields.Char(compute="_compute_custom_name", store=True, string="Tên hiển thị")

    def _merge_note(self, original_note, auto_note):
        if original_note:
            return f"{original_note}\n{auto_note}"
        return auto_note

    def _auto_close_allocations(self, allocations, release_date, source, auto_note):
        release_date = release_date or fields.Date.context_today(self)
        for allocation in allocations:
            allocation.with_context(skip_asset_allocation_automation=True).write({
                'trang_thai': 'not-in-use',
                'ngay_thu_hoi': release_date,
                'nguon_cap_nhat': source,
                'ghi_chu': allocation._merge_note(allocation.ghi_chu, auto_note),
            })

    def _auto_close_allocations_for_asset(self, asset_id, release_date, exclude_id=False):
        if not asset_id:
            return
        domain = [
            ('tai_san_id', '=', asset_id),
            ('trang_thai', '=', 'in-use'),
        ]
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        allocations = self.search(domain)
        auto_note = f'Tự động thu hồi do tài sản được cấp phát lại ngày {release_date}.'
        self._auto_close_allocations(allocations, release_date, 'auto_reallocation', auto_note)

    def _auto_close_employee_allocations_for_transfer(self, employee_id, department_id, release_date):
        if not employee_id or not department_id:
            return
        allocations = self.search([
            ('nhan_vien_su_dung_id', '=', employee_id),
            ('trang_thai', '=', 'in-use'),
            ('phong_ban_id', '!=', department_id),
        ])
        department = self.env['phong_ban'].browse(department_id)
        auto_note = f'Tự động thu hồi do nhân sự điều chuyển sang phòng ban {department.ten_phong_ban} từ ngày {release_date}.'
        self._auto_close_allocations(allocations, release_date, 'auto_hr_transfer', auto_note)

    @api.depends('phong_ban_id', 'tai_san_id')
    def _compute_custom_name(self):
        for record in self:
            phong_ban_code = record.tai_san_id.ma_tai_san or 'Mã phòng ban không xác định'
            tai_san_name = record.tai_san_id.ten_tai_san or 'Tài sản không xác định'
            record.custom_name = f"{phong_ban_code} - {tai_san_name}"

    @api.onchange('phong_ban_id')
    def _onchange_phong_ban_id(self):
        if self.phong_ban_id and not self.vi_tri_tai_san_id:
            self.vi_tri_tai_san_id = self.phong_ban_id
        if self.nhan_vien_su_dung_id and self.nhan_vien_su_dung_id.phong_ban_hien_tai_id != self.phong_ban_id:
            self.nhan_vien_su_dung_id = False

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('skip_asset_allocation_automation'):
            for vals in vals_list:
                allocation_status = vals.get('trang_thai', 'in-use')
                asset_id = vals.get('tai_san_id')
                release_date = fields.Date.to_date(vals.get('ngay_phat')) if vals.get('ngay_phat') else fields.Date.context_today(self)
                if allocation_status == 'in-use' and asset_id:
                    self._auto_close_allocations_for_asset(asset_id, release_date)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get('skip_asset_allocation_automation'):
            for record in self:
                allocation_status = vals.get('trang_thai', record.trang_thai)
                asset_id = vals.get('tai_san_id', record.tai_san_id.id)
                release_date = fields.Date.to_date(vals.get('ngay_phat')) if vals.get('ngay_phat') else (record.ngay_phat or fields.Date.context_today(self))
                if allocation_status == 'in-use' and asset_id:
                    self._auto_close_allocations_for_asset(asset_id, release_date, exclude_id=record.id)
        return super().write(vals)

    @api.constrains('tai_san_id', 'trang_thai', 'nhan_vien_su_dung_id', 'phong_ban_id', 'ngay_phat')
    def _check_business_rules(self):
        for record in self:
            if record.trang_thai == 'in-use':
                duplicate_allocation = self.search_count([
                    ('id', '!=', record.id),
                    ('tai_san_id', '=', record.tai_san_id.id),
                    ('trang_thai', '=', 'in-use'),
                ])
                if duplicate_allocation:
                    raise ValidationError('Tài sản vẫn còn phân bổ đang sử dụng khác chưa được hệ thống đóng tự động.')

            if record.trang_thai == 'in-use' and record.nhan_vien_su_dung_id:
                if record.nhan_vien_su_dung_id.phong_ban_hien_tai_id != record.phong_ban_id:
                    raise ValidationError('Nhân viên sử dụng phải thuộc đúng phòng ban được phân bổ tài sản.')

                lich_su_hop_le = self.env['lich_su_cong_tac'].search_count([
                    ('nhan_vien_id', '=', record.nhan_vien_su_dung_id.id),
                    ('phong_ban_id', '=', record.phong_ban_id.id),
                    ('time_start', '<=', record.ngay_phat),
                    ('time_end', '>=', record.ngay_phat),
                ])
                if not lich_su_hop_le:
                    raise ValidationError('Không tìm thấy lịch sử công tác hợp lệ của nhân viên tại phòng ban vào ngày phân bổ.')