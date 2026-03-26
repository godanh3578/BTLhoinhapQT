# Quản lý văn bản

## Liên kết với module Nhân sự

Module này phụ thuộc `nhan_su` và mở rộng model `nhan_vien` để liên kết hồ sơ nhân sự với văn bản đến.

### Trường liên kết trên văn bản

* `nhan_vien_xu_ly_id`: Cán bộ xử lý
* `nhan_vien_ky_id`: Người ký
* `nhan_vien_nhan_ids`: Người nhận hoặc phối hợp

### Thông tin hiển thị trên hồ sơ nhân viên

* Smart button mở danh sách văn bản liên quan
* Tab văn bản xử lý
* Tab văn bản ký
* Tab văn bản nhận hoặc phối hợp

### Dependency đúng

```python
# addons/nhan_su/__manifest__.py
'depends': ['base']

# addons/quan_ly_van_ban/__manifest__.py
'depends': ['base', 'nhan_su']
```

Không cấu hình `nhan_su` phụ thuộc ngược lại `quan_ly_van_ban`, vì Odoo không cho phép phụ thuộc vòng giữa hai addon.