from odoo import api, fields, models
from odoo.exceptions import ValidationError


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

    def _get_currency_code(self):
        self.ensure_one()
        currency_name = (self.currency_id.name or '').upper()
        if currency_name == 'USD':
            return 'usd'
        if currency_name in {'VND', 'VNĐ'}:
            return 'vnd'
        raise ValidationError('Hiện tại chỉ hỗ trợ tự động tạo tài sản cho chứng từ dùng tiền tệ VND hoặc USD.')

    def _get_request_lines(self):
        self.ensure_one()
        lines = self.de_nghi_mua_sam_id.line_ids
        if not lines:
            raise ValidationError('Đề nghị mua sắm chưa có hạng mục để hình thành bút toán và tài sản.')
        return lines

    def _validate_automation_configuration(self, lines):
        self.ensure_one()
        funding_source = self.de_nghi_mua_sam_id.nguon_kinh_phi_id
        if not funding_source:
            raise ValidationError('Cần chọn nguồn kinh phí trước khi ghi nhận chứng từ.')
        if not funding_source.purchase_journal_id:
            raise ValidationError('Nguồn kinh phí chưa cấu hình sổ nhật ký mua tài sản.')
        if not funding_source.clearing_account_id:
            raise ValidationError('Nguồn kinh phí chưa cấu hình tài khoản đối ứng nguồn vốn.')

        asset_total = 0.0
        for line in lines:
            if line.co_hinh_thanh_tai_san:
                if not line.danh_muc_ts_id:
                    raise ValidationError(f'Hạng mục {line.ten_hang_muc} chưa có loại tài sản.')
                if not line.danh_muc_ts_id.asset_account_id:
                    raise ValidationError(f'Loại tài sản của hạng mục {line.ten_hang_muc} chưa có tài khoản nguyên giá.')
                rounded_quantity = round(line.so_luong)
                if abs(line.so_luong - rounded_quantity) > 1e-6:
                    raise ValidationError(
                        f'Hạng mục {line.ten_hang_muc} phải có số lượng nguyên để tự động sinh từng tài sản.'
                    )
            elif not funding_source.expense_account_id:
                raise ValidationError(
                    'Nguồn kinh phí chưa cấu hình tài khoản chi phí cho hạng mục không hình thành tài sản.'
                )
            asset_total += line.thanh_tien_du_kien

        if round(asset_total, 2) != round(self.gia_tri_thanh_toan, 2):
            raise ValidationError(
                'Tổng giá trị các hạng mục phải khớp với giá trị thanh toán để hệ thống tự động tạo bút toán kế toán.'
            )

    def _prepare_move_line_vals(self, lines):
        self.ensure_one()
        grouped_lines = {}
        funding_source = self.de_nghi_mua_sam_id.nguon_kinh_phi_id
        for line in lines:
            account = line.danh_muc_ts_id.asset_account_id if line.co_hinh_thanh_tai_san else funding_source.expense_account_id
            key = account.id
            if key not in grouped_lines:
                grouped_lines[key] = {
                    'name': f'Ghi nhận mua sắm từ {self.so_chung_tu}',
                    'account_id': account.id,
                    'debit': 0.0,
                    'credit': 0.0,
                }
            grouped_lines[key]['debit'] += line.thanh_tien_du_kien

        move_lines = [(0, 0, values) for values in grouped_lines.values()]
        move_lines.append((0, 0, {
            'name': f'Đối ứng nguồn vốn {funding_source.ten_nguon}',
            'account_id': funding_source.clearing_account_id.id,
            'debit': 0.0,
            'credit': self.gia_tri_thanh_toan,
        }))
        return move_lines

    def _create_account_move(self):
        self.ensure_one()
        if self.account_move_id:
            return self.account_move_id
        lines = self._get_request_lines()
        self._validate_automation_configuration(lines)
        journal = self.de_nghi_mua_sam_id.nguon_kinh_phi_id.purchase_journal_id
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': self.ngay_chung_tu,
            'journal_id': journal.id,
            'ref': f'Mua tài sản {self.so_chung_tu}',
            'line_ids': self._prepare_move_line_vals(lines),
        })
        move.action_post()
        return move

    def _split_amounts(self, total_amount, quantity):
        unit_amount = round(total_amount / quantity, 2)
        amounts = [unit_amount] * quantity
        amounts[-1] = round(total_amount - sum(amounts[:-1]), 2)
        return amounts

    def _auto_create_assets(self):
        self.ensure_one()
        if self.tai_san_ids:
            return self.tai_san_ids
        asset_model = self.env['tai_san']
        currency_code = self._get_currency_code()
        created_assets = self.env['tai_san']
        for line in self._get_request_lines().filtered('co_hinh_thanh_tai_san'):
            quantity = int(round(line.so_luong))
            amounts = self._split_amounts(line.thanh_tien_du_kien, quantity)
            for index, amount in enumerate(amounts, start=1):
                asset_code = self.env['ir.sequence'].next_by_code('tai_san_auto') or f'TSAUTO/{fields.Date.today().year}/{index:04d}'
                asset_name = line.ten_hang_muc if quantity == 1 else f'{line.ten_hang_muc} #{index}'
                created_assets |= asset_model.create({
                    'ma_tai_san': asset_code,
                    'ten_tai_san': asset_name,
                    'ngay_mua_ts': self.ngay_chung_tu,
                    'don_vi_tien_te': currency_code,
                    'gia_tri_ban_dau': amount,
                    'gia_tri_hien_tai': amount,
                    'danh_muc_ts_id': line.danh_muc_ts_id.id,
                    'don_vi_tinh': 'Chiếc',
                    'ghi_chu': f'Tự động tạo từ chứng từ {self.so_chung_tu}',
                    'de_nghi_mua_sam_id': self.de_nghi_mua_sam_id.id,
                    'chung_tu_mua_sam_id': self.id,
                    'ngay_ghi_tang': self.ngay_chung_tu,
                    'dia_diem_su_dung': self.de_nghi_mua_sam_id.phong_ban_id.ten_phong_ban,
                })
        return created_assets

    def action_mark_posted(self):
        for record in self:
            move = record._create_account_move()
            record._auto_create_assets()
            record.write({'trang_thai': 'posted', 'account_move_id': move.id})
            record.de_nghi_mua_sam_id.write({'trang_thai': 'purchased'})
            record.de_nghi_mua_sam_id._send_telegram_notifications('document_posted')
        return True

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