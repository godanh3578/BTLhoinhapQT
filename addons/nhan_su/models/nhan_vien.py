from datetime import timedelta

from odoo import api, fields, models


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_ten'
    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh đã tồn tại.'),
    ]

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten = fields.Char("Họ tên", required=True, default='')
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    user_id = fields.Many2one('res.users', string='Người dùng hệ thống', ondelete='set null')
    ngay_nhan_cong_tac = fields.Date("Ngày nhận công tác hiện tại", default=fields.Date.context_today)
    lich_su_cong_tac_ids = fields.One2many("lich_su_cong_tac", string="Danh sách lịch sử công tác", inverse_name="nhan_vien_id")
    phong_ban_hien_tai_id = fields.Many2one('phong_ban', string='Phòng ban hiện tại', ondelete='restrict')
    chuc_vu_hien_tai_id = fields.Many2one('chuc_vu', string='Chức vụ hiện tại', ondelete='restrict')
    vai_tro_he_thong = fields.Selection(related='chuc_vu_hien_tai_id.vai_tro_he_thong', string='Vai trò hệ thống', readonly=True)
    duoc_tao_giao_dich_tai_chinh = fields.Boolean(related='chuc_vu_hien_tai_id.duoc_tao_giao_dich_tai_chinh', readonly=True)
    duoc_phe_duyet_tai_chinh = fields.Boolean(related='chuc_vu_hien_tai_id.duoc_phe_duyet_tai_chinh', readonly=True)
    duoc_ghi_so_ke_toan = fields.Boolean(related='chuc_vu_hien_tai_id.duoc_ghi_so_ke_toan', readonly=True)
    han_muc_phe_duyet_tai_chinh = fields.Float(related='chuc_vu_hien_tai_id.han_muc_phe_duyet_tai_chinh', readonly=True)
    so_tai_san_dang_su_dung = fields.Integer(string='Số tài sản đang sử dụng', compute='_compute_so_tai_san_dang_su_dung', store=True)
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)

    # ids_van_ban_di = fields.One2many(comodel_name='van_ban_di', inverse_name='id_nguoi_phat_hanh', string="Số văn bản đi")

    @api.depends('ngay_sinh')
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                record.tuoi = (fields.Date.today() - record.ngay_sinh).days // 365
            else:
                record.tuoi = 0

    @api.depends('ma_dinh_danh')
    def _compute_so_tai_san_dang_su_dung(self):
        phan_bo_model = self.env.get('phan_bo_tai_san')
        for record in self:
            if not phan_bo_model:
                record.so_tai_san_dang_su_dung = 0
                continue
            record.so_tai_san_dang_su_dung = phan_bo_model.search_count([
                ('nhan_vien_su_dung_id', '=', record.id),
                ('trang_thai', '=', 'in-use'),
            ])

    def _prepare_current_assignment_dates(self, vals):
        effective_date = vals.get('ngay_nhan_cong_tac')
        if effective_date:
            return fields.Date.to_date(effective_date)
        return fields.Date.to_date(fields.Date.context_today(self))

    @api.model
    def _get_employee_from_user(self, user=False):
        current_user = user or self.env.user
        return self.search([('user_id', '=', current_user.id)], limit=1)

    @api.model
    def _find_finance_approver(self, amount, department_id=False, exclude_employee_id=False):
        domain = [('chuc_vu_hien_tai_id.duoc_phe_duyet_tai_chinh', '=', True)]
        if exclude_employee_id:
            domain.append(('id', '!=', exclude_employee_id))

        candidates = self.search(domain)
        if department_id:
            department_candidates = candidates.filtered(lambda employee: employee.phong_ban_hien_tai_id.id == department_id)
            if department_candidates:
                candidates = department_candidates

        candidates = candidates.filtered(
            lambda employee: not employee.han_muc_phe_duyet_tai_chinh or employee.han_muc_phe_duyet_tai_chinh >= amount
        )
        return candidates.sorted(
            key=lambda employee: (
                1 if employee.vai_tro_he_thong == 'director' else 0,
                employee.han_muc_phe_duyet_tai_chinh or 0.0,
            ),
            reverse=True,
        )[:1]

    @api.model
    def _find_accountant_employee(self, department_id=False):
        candidates = self.search([('chuc_vu_hien_tai_id.duoc_ghi_so_ke_toan', '=', True)])
        if department_id:
            department_candidates = candidates.filtered(lambda employee: employee.phong_ban_hien_tai_id.id == department_id)
            if department_candidates:
                candidates = department_candidates
        return candidates[:1]

    def _sync_current_assignment_history(self, vals=None):
        if self.env.context.get('skip_assignment_history_sync'):
            return
        history_model = self.env['lich_su_cong_tac']
        vals = vals or {}

        for record in self:
            if not record.phong_ban_hien_tai_id or not record.chuc_vu_hien_tai_id:
                continue

            effective_date = record.ngay_nhan_cong_tac or self._prepare_current_assignment_dates(vals)
            if isinstance(effective_date, str):
                effective_date = fields.Date.to_date(effective_date)

            open_history = history_model.search([
                ('nhan_vien_id', '=', record.id),
                ('time_end', '=', False),
            ], order='time_start desc, id desc', limit=1)

            if open_history and (
                open_history.phong_ban_id != record.phong_ban_hien_tai_id
                or open_history.chuc_vu_id != record.chuc_vu_hien_tai_id
            ):
                open_history.with_context(skip_assignment_history_sync=True).write({
                    'time_end': effective_date - timedelta(days=1),
                })
                open_history = self.env['lich_su_cong_tac']

            if open_history:
                update_vals = {}
                if open_history.time_start != effective_date:
                    update_vals['time_start'] = effective_date
                if open_history.phong_ban_id != record.phong_ban_hien_tai_id:
                    update_vals['phong_ban_id'] = record.phong_ban_hien_tai_id.id
                if open_history.chuc_vu_id != record.chuc_vu_hien_tai_id:
                    update_vals['chuc_vu_id'] = record.chuc_vu_hien_tai_id.id
                if update_vals:
                    open_history.with_context(skip_assignment_history_sync=True).write(update_vals)
            else:
                history_model.with_context(skip_assignment_history_sync=True).create({
                    'nhan_vien_id': record.id,
                    'phong_ban_id': record.phong_ban_hien_tai_id.id,
                    'chuc_vu_id': record.chuc_vu_hien_tai_id.id,
                    'time_start': effective_date,
                })

    def _run_department_transfer_automation(self, vals=None):
        phan_bo_model = self.env.get('phan_bo_tai_san')
        if not phan_bo_model:
            return

        vals = vals or {}
        effective_date = self._prepare_current_assignment_dates(vals)
        for record in self.filtered('phong_ban_hien_tai_id'):
            phan_bo_model._auto_close_employee_allocations_for_transfer(
                record.id,
                record.phong_ban_hien_tai_id.id,
                effective_date,
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record, vals in zip(records, vals_list):
            record._sync_current_assignment_history(vals)
            if vals.get('phong_ban_hien_tai_id'):
                record._run_department_transfer_automation(vals)
        return records

    def write(self, vals):
        tracked_fields = {'phong_ban_hien_tai_id', 'chuc_vu_hien_tai_id', 'ngay_nhan_cong_tac'}
        should_sync = bool(tracked_fields.intersection(vals))
        result = super().write(vals)
        if should_sync:
            self._sync_current_assignment_history(vals)
            if vals.get('phong_ban_hien_tai_id'):
                self._run_department_transfer_automation(vals)
        return result


