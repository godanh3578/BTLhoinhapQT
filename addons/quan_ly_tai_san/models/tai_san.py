import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)

class TaiSan(models.Model):
    _name = 'tai_san'
    _description = 'Bảng chứa thông tin tài sản'
    _rec_name = 'cus_rec_name'
    _order = 'ngay_mua_ts desc'
    _sql_constraints = [
        ("ma_tai_san_unique", "unique(ma_tai_san)", "Mã tài sản đã tồn tại !"),
    ]


    ma_tai_san = fields.Char('Mã tài sản', required=True)
    ten_tai_san = fields.Char('Tên tài sản', required=True)
    ngay_mua_ts = fields.Date('Ngày mua tài sản', required=True)
    don_vi_tien_te = fields.Selection([
        ('vnd', 'VNĐ'),
        ('usd', '$'),
    ], string='Đơn vị tiền tệ', default='vnd', required=True)
    gia_tri_ban_dau = fields.Float('Giá trị ban đầu', default = 1, required=True)
    gia_tri_hien_tai = fields.Float('Giá trị hiện tại', default = 1, required=True)
    danh_muc_ts_id = fields.Many2one('danh_muc_tai_san', string='Loại tài sản', required=True, ondelete='restrict')
    giay_to_tai_san = fields.Binary('Giấy tờ liên quan', attachment=True)
    giay_to_tai_san_filename = fields.Char('Tên file')
    hinh_anh = fields.Image('Hình ảnh', max_width=200, max_height=200)

    pp_khau_hao = fields.Selection([
        ('straight-line', 'Tuyến tính'),
        ('degressive', 'Giảm dần'),
        ('none', 'Không')
    ], string='Phương pháp khấu hao', default = 'none', required=True)
    thoi_gian_su_dung = fields.Integer('Thời gian đã sử dụng (năm)', default=0)

    # Khấu hao tuyến tính
    thoi_gian_toi_da = fields.Integer('Thời gian sử dụng còn lại tối đa (năm)', default=5)

    # Khấu hao giảm dần
    ty_le_khau_hao = fields.Float('Tỷ lệ khấu hao (%)', default=20)
    so_thang_da_khau_hao = fields.Integer('Số tháng đã khấu hao', default=0, readonly=True)
    chu_ky_khau_hao_thang = fields.Integer('Chu kỳ khấu hao (tháng)', default=1, required=True)
    ngay_bat_dau_khau_hao = fields.Date('Ngày bắt đầu khấu hao', default=lambda self: fields.Date.context_today(self))
    gia_tri_da_khau_hao = fields.Float('Giá trị đã khấu hao', compute='_compute_gia_tri_da_khau_hao', store=True)
    ngay_khau_hao_tiep_theo = fields.Date('Ngày khấu hao tiếp theo', compute='_compute_ngay_khau_hao_tiep_theo', store=True)

    don_vi_tinh = fields.Char('Đơn vị tính', default = 'Chiếc', required=True)
    ghi_chu = fields.Char('Ghi chú')

    cus_rec_name = fields.Char(compute='_compute_cus_rec_name', store=True)
    @api.depends('ten_tai_san', 'ma_tai_san')
    def _compute_cus_rec_name(self):
        for record in self:
            record.cus_rec_name = record.ma_tai_san + ' - ' + record.ten_tai_san

    phong_ban_su_dung_ids = fields.One2many('phan_bo_tai_san', 'tai_san_id', string='Phòng ban sử dụng')
    lich_su_khau_hao_ids = fields.One2many('lich_su_khau_hao', 'ma_ts', string='Lịch sử khấu hao')
    phong_ban_hien_tai_id = fields.Many2one('phong_ban', string='Phòng ban hiện tại', compute='_compute_current_allocation', store=True)
    nhan_vien_hien_tai_id = fields.Many2one('nhan_vien', string='Nhân viên đang sử dụng', compute='_compute_current_allocation', store=True)
    ngay_khau_hao_gan_nhat = fields.Date(string='Ngày khấu hao gần nhất', compute='_compute_ngay_khau_hao_gan_nhat', store=True)
    trang_thai_tai_san = fields.Selection([
        ('draft', 'Chưa phân bổ'),
        ('in_use', 'Đang sử dụng'),
        ('depreciated', 'Đã khấu hao hết'),
    ], string='Trạng thái', compute='_compute_trang_thai_tai_san', store=True)
    
    @api.depends('gia_tri_hien_tai', 'phong_ban_su_dung_ids.trang_thai')
    def _compute_trang_thai_tai_san(self):
        for record in self:
            if record.gia_tri_hien_tai <= 0:
                record.trang_thai_tai_san = 'depreciated'
            elif any(line.trang_thai == 'in-use' for line in record.phong_ban_su_dung_ids):
                record.trang_thai_tai_san = 'in_use'
            else:
                record.trang_thai_tai_san = 'draft'

    @api.depends(
        'phong_ban_su_dung_ids.trang_thai',
        'phong_ban_su_dung_ids.ngay_phat',
        'phong_ban_su_dung_ids.phong_ban_id',
        'phong_ban_su_dung_ids.nhan_vien_su_dung_id',
    )
    def _compute_current_allocation(self):
        for record in self:
            current_allocation = record.phong_ban_su_dung_ids.filtered(lambda item: item.trang_thai == 'in-use').sorted(
                key=lambda item: item.ngay_phat or fields.Date.today(),
                reverse=True,
            )[:1]
            record.phong_ban_hien_tai_id = current_allocation.phong_ban_id if current_allocation else False
            record.nhan_vien_hien_tai_id = current_allocation.nhan_vien_su_dung_id if current_allocation else False

    @api.depends('lich_su_khau_hao_ids.ngay_khau_hao')
    def _compute_ngay_khau_hao_gan_nhat(self):
        for record in self:
            khau_hao_moi_nhat = record.lich_su_khau_hao_ids.sorted('ngay_khau_hao', reverse=True)[:1]
            record.ngay_khau_hao_gan_nhat = khau_hao_moi_nhat.ngay_khau_hao.date() if khau_hao_moi_nhat.ngay_khau_hao else False

    @api.depends('gia_tri_ban_dau', 'gia_tri_hien_tai')
    def _compute_gia_tri_da_khau_hao(self):
        for record in self:
            record.gia_tri_da_khau_hao = max(record.gia_tri_ban_dau - record.gia_tri_hien_tai, 0)

    @api.depends('ngay_bat_dau_khau_hao', 'ngay_khau_hao_gan_nhat', 'chu_ky_khau_hao_thang', 'pp_khau_hao', 'gia_tri_hien_tai')
    def _compute_ngay_khau_hao_tiep_theo(self):
        for record in self:
            if record.pp_khau_hao == 'none' or record.gia_tri_hien_tai <= 0 or not record.ngay_bat_dau_khau_hao:
                record.ngay_khau_hao_tiep_theo = False
                continue

            base_date = record.ngay_khau_hao_gan_nhat or record.ngay_bat_dau_khau_hao
            if record.ngay_khau_hao_gan_nhat:
                record.ngay_khau_hao_tiep_theo = base_date + relativedelta(months=record.chu_ky_khau_hao_thang)
            else:
                record.ngay_khau_hao_tiep_theo = record.ngay_bat_dau_khau_hao

    @api.constrains('gia_tri_ban_dau', 'gia_tri_hien_tai', 'chu_ky_khau_hao_thang', 'ngay_bat_dau_khau_hao')
    def _check_gia_tri(self):
        for record in self:
            if record.gia_tri_ban_dau < 0 or record.gia_tri_hien_tai < 0:
                raise ValidationError("Giá trị (ban đầu, hiện tại) không thể âm !")
            elif record.gia_tri_hien_tai > record.gia_tri_ban_dau:
                raise ValidationError("Giá trị hiện tại không thể lớn hơn giá trị ban đầu !")
            elif record.chu_ky_khau_hao_thang <= 0:
                raise ValidationError('Chu kỳ khấu hao phải lớn hơn 0 tháng.')
            elif record.pp_khau_hao != 'none' and not record.ngay_bat_dau_khau_hao:
                raise ValidationError('Cần nhập ngày bắt đầu khấu hao cho tài sản có khấu hao.')

    @api.constrains('pp_khau_hao', 'danh_muc_ts_id')
    def _check_accounting_configuration_for_depreciation(self):
        for record in self:
            if record.pp_khau_hao != 'none':
                record._validate_accounting_configuration()

    def _get_monthly_depreciation_amount(self):
        self.ensure_one()
        if self.pp_khau_hao == 'none':
            raise ValidationError('Tài sản này không có phương pháp khấu hao.')
        if self.gia_tri_hien_tai <= 0:
            raise ValidationError('Tài sản đã hết giá trị khấu hao.')

        if self.pp_khau_hao == 'straight-line':
            if self.thoi_gian_toi_da <= 0:
                raise ValidationError('Thời gian sử dụng tối đa phải lớn hơn 0 năm.')
            so_tien_khau_hao = (self.gia_tri_ban_dau / (self.thoi_gian_toi_da * 12)) * self.chu_ky_khau_hao_thang
        else:
            if self.ty_le_khau_hao <= 0 or self.ty_le_khau_hao >= 100:
                raise ValidationError('Tỷ lệ khấu hao phải nằm trong khoảng (0, 100).')
            so_tien_khau_hao = self.gia_tri_hien_tai * (self.ty_le_khau_hao / 100) * (self.chu_ky_khau_hao_thang / 12)

        return round(min(so_tien_khau_hao, self.gia_tri_hien_tai), 2)

    def _validate_accounting_configuration(self):
        self.ensure_one()
        danh_muc = self.danh_muc_ts_id
        if not danh_muc.depreciation_journal_id:
            raise ValidationError('Loại tài sản chưa cấu hình sổ nhật ký khấu hao.')
        if not danh_muc.asset_account_id:
            raise ValidationError('Loại tài sản chưa cấu hình tài khoản nguyên giá tài sản.')
        if not danh_muc.depreciation_expense_account_id:
            raise ValidationError('Loại tài sản chưa cấu hình tài khoản chi phí khấu hao.')
        if not danh_muc.depreciation_accumulated_account_id:
            raise ValidationError('Loại tài sản chưa cấu hình tài khoản hao mòn lũy kế.')

    def _create_account_move(self, amount, depreciation_date, period_label):
        self.ensure_one()
        self._validate_accounting_configuration()
        journal = self.danh_muc_ts_id.depreciation_journal_id
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': depreciation_date,
            'journal_id': journal.id,
            'ref': f'Khấu hao {self.ma_tai_san} kỳ {period_label}',
            'line_ids': [
                (0, 0, {
                    'name': f'Chi phí khấu hao {self.ten_tai_san}',
                    'account_id': self.danh_muc_ts_id.depreciation_expense_account_id.id,
                    'debit': amount,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'name': f'Hao mòn lũy kế {self.ten_tai_san}',
                    'account_id': self.danh_muc_ts_id.depreciation_accumulated_account_id.id,
                    'debit': 0.0,
                    'credit': amount,
                }),
            ],
        })
        move.action_post()
        return move

    def _perform_monthly_depreciation(self, depreciation_date=False, raise_if_exists=True):
        lich_su_model = self.env['lich_su_khau_hao']
        depreciation_date = depreciation_date or fields.Date.context_today(self)
        if isinstance(depreciation_date, str):
            depreciation_date = fields.Date.to_date(depreciation_date)
        period_label = depreciation_date.strftime('%Y-%m')

        for record in self:
            if record.pp_khau_hao == 'none' or record.gia_tri_hien_tai <= 0:
                continue
            if not record.ngay_bat_dau_khau_hao or depreciation_date < record.ngay_bat_dau_khau_hao:
                continue
            if record.ngay_khau_hao_tiep_theo and depreciation_date < record.ngay_khau_hao_tiep_theo:
                continue

            ton_tai_ky = lich_su_model.search_count([
                ('ma_ts', '=', record.id),
                ('ky_khau_hao', '=', period_label),
            ])
            if ton_tai_ky:
                if raise_if_exists:
                    raise ValidationError(f'Tài sản {record.ten_tai_san} đã khấu hao cho kỳ {period_label}.')
                continue

            so_tien_khau_hao = record._get_monthly_depreciation_amount()
            but_toan = record._create_account_move(so_tien_khau_hao, depreciation_date, period_label)
            lich_su_model.create({
                'ma_phieu_khau_hao': f"KH-{record.ma_tai_san}-{period_label.replace('-', '')}",
                'ma_ts': record.id,
                'ngay_khau_hao': fields.Datetime.to_datetime(depreciation_date),
                'ky_khau_hao': period_label,
                'gia_tri_truoc_khau_hao': record.gia_tri_hien_tai,
                'so_tien_khau_hao': so_tien_khau_hao,
                'loai_phieu': 'automatic',
                'ghi_chu': f'Khấu hao tự động kỳ {period_label}',
                'but_toan_id': but_toan.id,
            })

    def action_tinh_khau_hao(self):
        self._perform_monthly_depreciation(raise_if_exists=True)
        return True

    @api.model
    def cron_tinh_khau_hao_hang_thang(self):
        tai_san_ids = self.search([
            ('pp_khau_hao', '!=', 'none'),
            ('gia_tri_hien_tai', '>', 0),
        ])
        for tai_san in tai_san_ids:
            try:
                tai_san._perform_monthly_depreciation(raise_if_exists=False)
            except ValidationError as error:
                _logger.warning('Không thể khấu hao tài sản %s: %s', tai_san.ma_tai_san, error)

