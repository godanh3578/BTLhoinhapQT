from odoo import models, fields, api


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
    lich_su_cong_tac_ids = fields.One2many("lich_su_cong_tac", string="Danh sách lịch sử công tác", inverse_name="nhan_vien_id")
    phong_ban_hien_tai_id = fields.Many2one('phong_ban', string='Phòng ban hiện tại', compute='_compute_cong_tac_hien_tai', store=True)
    chuc_vu_hien_tai_id = fields.Many2one('chuc_vu', string='Chức vụ hiện tại', compute='_compute_cong_tac_hien_tai', store=True)
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

    @api.depends(
        'lich_su_cong_tac_ids.time_start',
        'lich_su_cong_tac_ids.time_end',
        'lich_su_cong_tac_ids.phong_ban_id',
        'lich_su_cong_tac_ids.chuc_vu_id',
    )
    def _compute_cong_tac_hien_tai(self):
        for record in self:
            lich_su_hop_le = record.lich_su_cong_tac_ids.sorted(
                key=lambda item: (item.time_end or fields.Date.today(), item.time_start or fields.Date.today()),
                reverse=True,
            )
            current_history = lich_su_hop_le[:1]
            record.phong_ban_hien_tai_id = current_history.phong_ban_id if current_history else False
            record.chuc_vu_hien_tai_id = current_history.chuc_vu_id if current_history else False

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


