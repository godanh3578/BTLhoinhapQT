import json
import logging
from urllib import error, parse, request

from odoo import api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class FinanceIntegrationSettings(models.Model):
    _name = 'finance.integration.settings'
    _description = 'Cấu hình tích hợp AI và API ngoài'
    _rec_name = 'display_name'
    _sql_constraints = [
        ('company_unique', 'unique(company_id)', 'Mỗi công ty chỉ có một cấu hình tích hợp.'),
    ]

    company_id = fields.Many2one('res.company', string='Công ty', required=True, default=lambda self: self.env.company, ondelete='cascade')
    display_name = fields.Char('Tên cấu hình', compute='_compute_display_name', store=True)
    ai_enabled = fields.Boolean('Bật AI phân tích', default=True)
    ai_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('gemini', 'Gemini'),
    ], string='Nhà cung cấp AI', default='openai', required=True)
    ai_api_key = fields.Char('API key AI')
    ai_model = fields.Char('Model AI', default='gpt-4o-mini')
    ai_endpoint = fields.Char('AI endpoint tùy chỉnh')
    telegram_enabled = fields.Boolean('Bật Telegram', default=False)
    telegram_bot_token = fields.Char('Telegram bot token')
    telegram_chat_id = fields.Char('Telegram chat id')
    telegram_notify_on_approval = fields.Boolean('Thông báo khi phê duyệt đề nghị', default=True)
    telegram_notify_on_document = fields.Boolean('Thông báo khi ghi nhận chứng từ', default=True)

    @api.depends('company_id')
    def _compute_display_name(self):
        for record in self:
            company_name = record.company_id.name or 'Mặc định'
            record.display_name = f'Cấu hình tích hợp - {company_name}'

    @api.model
    def get_company_settings(self, company=False):
        company = company or self.env.company
        settings = self.search([('company_id', '=', company.id)], limit=1)
        if not settings:
            settings = self.create({'company_id': company.id})
        return settings

    def _prepare_ai_prompt(self, purchase_request):
        purchase_lines = '\n'.join(
            f"- {line.ten_hang_muc}: số lượng {line.so_luong}, đơn giá dự kiến {line.don_gia_du_kien:,.0f}, thành tiền {line.thanh_tien_du_kien:,.0f}, hình thành tài sản: {'Có' if line.co_hinh_thanh_tai_san else 'Không'}"
            for line in purchase_request.line_ids
        ) or '- Không có hạng mục'
        return (
            'Bạn là trợ lý tài chính nội bộ của doanh nghiệp. '
            'Hãy phân tích ngắn gọn bằng tiếng Việt cho một đề nghị mua sắm tài sản. '
            'Câu trả lời gồm 3 phần rõ ràng: 1) Đánh giá nhu cầu, 2) Rủi ro ngân sách và vận hành, 3) Đề xuất xử lý tiếp theo. '
            'Giữ văn phong súc tích, thực dụng, tối đa 220 từ.\n\n'
            f'Số đề nghị: {purchase_request.so_de_nghi}\n'
            f'Ngày đề nghị: {purchase_request.ngay_de_nghi}\n'
            f'Phòng ban: {purchase_request.phong_ban_id.ten_phong_ban}\n'
            f'Người đề nghị: {purchase_request.nguoi_de_nghi_id.ho_ten}\n'
            f'Ngân sách: {purchase_request.ngan_sach_id.ten_ngan_sach if purchase_request.ngan_sach_id else "Chưa có"}\n'
            f'Số tiền còn lại: {purchase_request.ngan_sach_id.so_tien_con_lai if purchase_request.ngan_sach_id else 0:,.0f}\n'
            f'Nguồn kinh phí: {purchase_request.nguon_kinh_phi_id.ten_nguon if purchase_request.nguon_kinh_phi_id else "Chưa có"}\n'
            f'Dự toán tổng: {purchase_request.du_toan_chi_phi:,.0f} {purchase_request.currency_id.name}\n'
            f'Nội dung: {purchase_request.noi_dung_mua_sam or "Không có mô tả"}\n'
            f'Hạng mục:\n{purchase_lines}'
        )

    def _call_openai(self, prompt):
        endpoint = self.ai_endpoint or 'https://api.openai.com/v1/chat/completions'
        payload = json.dumps({
            'model': self.ai_model or 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': 'Bạn trả lời bằng tiếng Việt, súc tích và theo ngữ cảnh ERP doanh nghiệp.'},
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.2,
        }).encode('utf-8')
        req = request.Request(
            endpoint,
            data=payload,
            headers={
                'Authorization': f'Bearer {self.ai_api_key}',
                'Content-Type': 'application/json',
            },
        )
        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        return data['choices'][0]['message']['content'].strip()

    def _call_gemini(self, prompt):
        model_name = self.ai_model or 'gemini-1.5-flash'
        endpoint = self.ai_endpoint or f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.ai_api_key}'
        payload = json.dumps({
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'temperature': 0.2},
        }).encode('utf-8')
        req = request.Request(endpoint, data=payload, headers={'Content-Type': 'application/json'})
        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        candidates = data.get('candidates') or []
        if not candidates:
            raise ValidationError('Gemini không trả về nội dung phân tích.')
        parts = candidates[0].get('content', {}).get('parts', [])
        return '\n'.join(part.get('text', '') for part in parts if part.get('text')).strip()

    def generate_purchase_request_analysis(self, purchase_request):
        self.ensure_one()
        if not self.ai_enabled:
            raise ValidationError('Cấu hình tích hợp chưa bật AI phân tích.')
        if not self.ai_api_key:
            raise ValidationError('Chưa cấu hình API key cho AI.')
        if not purchase_request.line_ids:
            raise ValidationError('Đề nghị chưa có hạng mục để AI phân tích.')

        prompt = self._prepare_ai_prompt(purchase_request)
        try:
            if self.ai_provider == 'gemini':
                return self._call_gemini(prompt)
            return self._call_openai(prompt)
        except error.HTTPError as http_error:
            message = http_error.read().decode('utf-8', errors='ignore')
            raise ValidationError(f'AI trả về lỗi HTTP {http_error.code}: {message}')
        except error.URLError as network_error:
            raise ValidationError(f'Không kết nối được tới dịch vụ AI: {network_error.reason}')
        except ValidationError:
            raise
        except Exception as unexpected_error:
            _logger.exception('Lỗi AI không mong đợi')
            raise ValidationError(f'Không thể hoàn tất phân tích AI: {unexpected_error}')

    def send_telegram_message(self, message, event_code=False):
        self.ensure_one()
        if not self.telegram_enabled:
            return False
        if event_code == 'approved' and not self.telegram_notify_on_approval:
            return False
        if event_code == 'document_posted' and not self.telegram_notify_on_document:
            return False
        if not self.telegram_bot_token or not self.telegram_chat_id:
            raise ValidationError('Telegram đã bật nhưng chưa cấu hình bot token hoặc chat id.')

        endpoint = f'https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage'
        payload = parse.urlencode({
            'chat_id': self.telegram_chat_id,
            'text': message,
        }).encode('utf-8')
        req = request.Request(endpoint, data=payload, method='POST')
        try:
            with request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
            if not result.get('ok'):
                raise ValidationError(f'Telegram từ chối yêu cầu: {result}')
            return True
        except error.HTTPError as http_error:
            message = http_error.read().decode('utf-8', errors='ignore')
            raise ValidationError(f'Telegram trả về lỗi HTTP {http_error.code}: {message}')
        except error.URLError as network_error:
            raise ValidationError(f'Không kết nối được tới Telegram: {network_error.reason}')

