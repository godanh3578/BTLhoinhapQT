# BTLhoinhapQT

## 1. Mục tiêu đề tài

Đề tài xây dựng hệ thống quản lý tài sản doanh nghiệp tích hợp với quản lý tài chính, kế toán và nhân sự trên nền tảng Odoo 15.

Hệ thống tập trung vào các yêu cầu chính:

1. Quản lý tài sản và phân bổ tài sản theo phòng ban, nhân viên
2. Tự động tính khấu hao hàng tháng và ghi nhận vào sổ cái kế toán
3. Quản lý ngân sách, nguồn kinh phí, đề nghị mua sắm và chứng từ mua tài sản
4. Tích hợp AI và External API trong xử lý nghiệp vụ

## 2. Phạm vi module

Hệ thống gồm ba module chính:

1. `nhan_su`
   Dữ liệu gốc về nhân viên, phòng ban, chức vụ và lịch sử công tác.

2. `quan_ly_tai_san`
   Quản lý tài sản, phân bổ sử dụng, thu hồi, khấu hao và liên kết kế toán.

3. `quan_ly_tai_chinh_ke_toan`
   Quản lý ngân sách, nguồn kinh phí, đề nghị mua sắm, chứng từ mua tài sản, AI phân tích và thông báo Telegram.

## 3. Nền tảng triển khai

Hệ thống được phát triển trên:

1. Odoo 15
2. Python
3. PostgreSQL
4. Docker Compose

## 4. Cài đặt và chạy hệ thống

### 4.1. Chuẩn bị môi trường

```bash
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libffi-dev zlib1g-dev python3.10-venv libpq-dev
python3.10 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4.2. Khởi tạo cơ sở dữ liệu

```bash
docker-compose up -d
```

### 4.3. Cấu hình Odoo

Tạo file `odoo.conf` với nội dung:

```ini
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5432
xmlrpc_port = 8069
```

### 4.4. Cài module

Sau khi truy cập `http://localhost:8069`, cài các module:

1. `nhan_su`
2. `quan_ly_tai_san`
3. `quan_ly_tai_chinh_ke_toan`

## 5. Luồng nghiệp vụ tích hợp

1. Dữ liệu HRM là nguồn gốc cho nhân viên và phòng ban.
2. Tài sản được phân bổ theo phòng ban và nhân viên đang thuộc phòng ban đó.
3. Hàng tháng hệ thống tự động tính khấu hao và sinh bút toán kế toán.
4. Khi ghi nhận chứng từ mua tài sản, hệ thống tự động tạo bút toán mua sắm và sinh tài sản từ các hạng mục hợp lệ.
5. Khi nhân sự điều chuyển phòng ban, các phân bổ tài sản không còn hợp lệ được tự động thu hồi.
6. Khi tài sản được cấp phát lại, hệ thống tự động đóng phân bổ cũ.

## 6. Mức độ đáp ứng theo yêu cầu

### Mức 1 - Tích hợp hệ thống

Đạt các yêu cầu:

1. Các module dùng chung một cơ sở dữ liệu
2. Dữ liệu HRM là dữ liệu gốc để đồng bộ sang tài sản và tài chính
3. Giảm nhập liệu trùng lặp giữa các module

### Mức 2 - Tự động hóa quy trình

Đạt các yêu cầu:

1. Cron tự động tính khấu hao hàng tháng và ghi nhận bút toán kế toán
2. Tự động đóng phân bổ cũ khi tài sản được cấp phát lại
3. Tự động thu hồi phân bổ khi HR điều chuyển nhân sự
4. Tự động tạo bút toán mua tài sản khi ghi nhận chứng từ
5. Tự động sinh tài sản từ chứng từ mua sắm

### Mức 3 - AI và External API

Đạt các yêu cầu khi đã cấu hình môi trường vận hành:

1. AI/LLM:
   Phân tích đề nghị mua sắm bằng OpenAI hoặc Gemini

2. External API:
   Gửi thông báo Telegram khi đề nghị được phê duyệt hoặc khi chứng từ mua tài sản được ghi nhận

## 7. Điều kiện vận hành mức 3

Để sử dụng đầy đủ tính năng AI và External API, cần cấu hình:

1. API key OpenAI hoặc Gemini
2. Telegram bot token
3. Telegram chat id
4. Journal và account kế toán cho loại tài sản, nguồn kinh phí

## 8. Tài liệu nộp bài

1. Phân tích nghiệp vụ: `docs/phan_tich_nghiep_vu_quan_ly_tai_san_ke_toan_hrm.md`
2. Phân rã yêu cầu: `docs/phan_ra_yeu_cau_3_module.md`
3. Business flow: `docs/business flow/Nhom6_BusinessFlow_QuanLyTaiSanKeToanHRM.png`
4. Poster: `docs/poster/Nhom6_Poster_QuanLyTaiSanKeToanHRM.png`
