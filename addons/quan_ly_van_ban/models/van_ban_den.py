from odoo import api, fields, models


class VanBanDen(models.Model):
	_name = 'van_ban_den'
	_description = 'Văn bản đến'
	_order = 'ngay_van_ban desc, id desc'
	_rec_name = 'display_name'

	so_van_ban = fields.Char('Số văn bản', required=True)
	ten_van_ban = fields.Char('Tên văn bản', required=True)
	ngay_van_ban = fields.Date('Ngày văn bản', required=True, default=fields.Date.context_today)
	han_xu_ly = fields.Date('Hạn xử lý')
	trich_yeu = fields.Text('Trích yếu')
	trang_thai = fields.Selection([
		('draft', 'Mới tạo'),
		('processing', 'Đang xử lý'),
		('done', 'Hoàn tất'),
	], string='Trạng thái', default='draft', required=True)
	nhan_vien_xu_ly_id = fields.Many2one(
		'nhan_vien',
		string='Cán bộ xử lý',
		required=True,
		ondelete='restrict',
	)
	nhan_vien_ky_id = fields.Many2one(
		'nhan_vien',
		string='Người ký',
		ondelete='restrict',
	)
	nhan_vien_nhan_ids = fields.Many2many(
		'nhan_vien',
		'van_ban_den_nhan_vien_rel',
		'van_ban_id',
		'nhan_vien_id',
		string='Người nhận/phối hợp',
	)
	display_name = fields.Char(compute='_compute_display_name', store=True)

	_sql_constraints = [
		('so_van_ban_unique', 'unique(so_van_ban)', 'Số văn bản đã tồn tại.'),
	]

	@api.depends('so_van_ban', 'ten_van_ban')
	def _compute_display_name(self):
		for record in self:
			if record.so_van_ban and record.ten_van_ban:
				record.display_name = f'{record.so_van_ban} - {record.ten_van_ban}'
			else:
				record.display_name = record.ten_van_ban or record.so_van_ban or 'Văn bản đến'
