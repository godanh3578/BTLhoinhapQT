from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LichSuCongTac(models.Model):
    _name = 'lich_su_cong_tac'
    _description = 'Bảng chứa thông tin lịch sử công tác'
    
    time_start = fields.Date("Thời gian bắt đầu", required=True, default=lambda self: fields.Date.today())
    time_end = fields.Date("Thời gian kết thúc")
    phong_ban_id = fields.Many2one("phong_ban",string="Phòng ban", required=True)
    chuc_vu_id = fields.Many2one("chuc_vu",string="Chức vụ", required=True)
    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân viên", required=True)
    ghi_chu = fields.Char("Ghi chú")

    @api.constrains('time_start', 'time_end')
    def _check_time_range(self):
        for record in self:
            if record.time_start and record.time_end and record.time_end < record.time_start:
                raise ValidationError('Thời gian kết thúc không được nhỏ hơn thời gian bắt đầu.')

    def _sync_employee_current_assignment(self):
        if self.env.context.get('skip_assignment_history_sync'):
            return

        today = fields.Date.to_date(fields.Date.context_today(self))
        for record in self:
            if not record.nhan_vien_id or not record.time_start or record.time_start > today:
                continue
            if record.time_end and record.time_end < today:
                continue

            record.nhan_vien_id.with_context(skip_assignment_history_sync=True).write({
                'phong_ban_hien_tai_id': record.phong_ban_id.id,
                'chuc_vu_hien_tai_id': record.chuc_vu_id.id,
                'ngay_nhan_cong_tac': record.time_start,
            })

    def _run_transfer_asset_automation(self):
        if 'phan_bo_tai_san' not in self.env.registry:
            return
        phan_bo_model = self.env['phan_bo_tai_san']

        today = fields.Date.to_date(fields.Date.context_today(self))
        for record in self:
            if not record.time_start:
                continue
            if record.time_start <= today and (not record.time_end or today <= record.time_end):
                phan_bo_model._auto_close_employee_allocations_for_transfer(
                    record.nhan_vien_id.id,
                    record.phong_ban_id.id,
                    record.time_start,
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_employee_current_assignment()
        records._run_transfer_asset_automation()
        return records

    def write(self, vals):
        result = super().write(vals)
        self._sync_employee_current_assignment()
        self._run_transfer_asset_automation()
        return result