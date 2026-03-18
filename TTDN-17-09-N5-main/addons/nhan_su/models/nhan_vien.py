from odoo import models, fields, api  


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_ten'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten = fields.Char("Họ tên", required=True, default='')
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    lich_su_cong_tac_ids = fields.One2many("lich_su_cong_tac",string="Danh sách lịch sử công tác", inverse_name="nhan_vien_id")
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)

    # ids_van_ban_di = fields.One2many(comodel_name='van_ban_di', inverse_name='id_nguoi_phat_hanh', string="Số văn bản đi")

    @api.depends('ngay_sinh')
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                record.tuoi = (fields.Date.today() - record.ngay_sinh).days // 365

    def unlink(self):
        # Khi xóa nhân viên, cập nhật trạng thái tài sản liên quan
        phan_bo_env = self.env['phan_bo_tai_san']
        for nhan_vien in self:
            phan_bos = phan_bo_env.search([('nhan_vien_su_dung_id', '=', nhan_vien.id), ('trang_thai', '=', 'in-use')])
            for pb in phan_bos:
                pb.trang_thai = 'not-in-use'
        return super(NhanVien, self).unlink()

    def write(self, vals):
        # Nếu trạng thái nhân viên có trường trạng_thai và chuyển sang nghỉ việc, cập nhật tài sản liên quan
        res = super(NhanVien, self).write(vals)
        if 'trang_thai' in vals and vals['trang_thai'] == 'nghi_viec':
            phan_bo_env = self.env['phan_bo_tai_san']
            for nhan_vien in self:
                phan_bos = phan_bo_env.search([('nhan_vien_su_dung_id', '=', nhan_vien.id), ('trang_thai', '=', 'in-use')])
                for pb in phan_bos:
                    pb.trang_thai = 'not-in-use'
        return res


