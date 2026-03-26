from odoo import api, fields, models


class NhanVien(models.Model):
    _inherit = 'nhan_vien'

    van_ban_den_xu_ly_ids = fields.One2many(
        'van_ban_den',
        'nhan_vien_xu_ly_id',
        string='Văn bản phụ trách',
    )
    van_ban_den_ky_ids = fields.One2many(
        'van_ban_den',
        'nhan_vien_ky_id',
        string='Văn bản đã ký',
    )
    van_ban_den_nhan_ids = fields.Many2many(
        'van_ban_den',
        compute='_compute_van_ban_den_nhan_ids',
        string='Văn bản nhận/phối hợp',
    )
    van_ban_den_count = fields.Integer(
        string='Số văn bản liên quan',
        compute='_compute_van_ban_den_count',
    )

    def _compute_van_ban_den_nhan_ids(self):
        for record in self:
            record.van_ban_den_nhan_ids = self.env['van_ban_den'].search([
                ('nhan_vien_nhan_ids', 'in', record.id),
            ])

    def _compute_van_ban_den_count(self):
        for record in self:
            record.van_ban_den_count = self.env['van_ban_den'].search_count([
                '|',
                '|',
                ('nhan_vien_xu_ly_id', '=', record.id),
                ('nhan_vien_ky_id', '=', record.id),
                ('nhan_vien_nhan_ids', 'in', record.id),
            ])

    def action_open_van_ban_den(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Văn bản đến',
            'res_model': 'van_ban_den',
            'view_mode': 'tree,form',
            'domain': [
                '|',
                '|',
                ('nhan_vien_xu_ly_id', '=', self.id),
                ('nhan_vien_ky_id', '=', self.id),
                ('nhan_vien_nhan_ids', 'in', self.id),
            ],
            'context': {
                'default_nhan_vien_xu_ly_id': self.id,
            },
        }