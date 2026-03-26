---
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)




# 1. Cài đặt công cụ, môi trường và các thư viện cần thiết

## 1.1. Clone project.
git clone https://gitlab.com/anhlta/odoo-fitdnu.git
git checkout 

## 1.2. cài đặt các thư viện cần thiết

Người sử dụng thực thi các lệnh sau đề cài đặt các thư viện cần thiết

```
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev python3.10-distutils python3.10-dev build-essential libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```
## 1.3. khởi tạo môi trường ảo.

`python3.10 -m venv ./venv`
Thay đổi trình thông dịch sang môi trường ảo và chạy requirements.txt để cài đặt tiếp các thư viện được yêu cầu

```
source venv/bin/activate
pip3 install -r requirements.txt
```

# 2. Setup database

Khởi tạo database trên docker bằng việc thực thi file dockercompose.yml.

`docker-compose up -d`

# 3. Setup tham số chạy cho hệ thống

## 3.1. Khởi tạo odoo.conf

Tạo tệp **odoo.conf** có nội dung như sau:

```
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5432
xmlrpc_port = 8069
```
Có thể kế thừa từ **odoo.conf.template**

Ngoài ra có thể thêm mổ số parameters như:

```
-c _<đường dẫn đến tệp odoo.conf>_
-u _<tên addons>_ giúp cập nhật addons đó trước khi khởi chạy
-d _<tên database>_ giúp chỉ rõ tên database được sử dụng
--dev=all giúp bật chế độ nhà phát triển 
```

# 4. Chạy hệ thống và cài đặt các ứng dụng cần thiết

Người sử dụng truy cập theo đường dẫn _http://localhost:8069/_ để đăng nhập vào hệ thống.

Hoàn tất

## Luồng nghiệp vụ tích hợp HRM - Tài sản - Kế toán

Luồng chính của đề tài Quản lý tài sản + Tài chính/Kế toán + HRM được mô tả tại `docs/business flow/NhomXX_BusinessFlow_QuanLyTaiSanKeToanHRM.png`, trong đó dữ liệu nhân sự từ module `nhan_su` là dữ liệu gốc để phân bổ tài sản, theo dõi người sử dụng và ghi nhận khấu hao vào sổ cái kế toán.

Poster giới thiệu hệ thống được đặt tại `docs/poster/NhomXX_Poster_QuanLyTaiSanKeToanHRM.png`, tóm tắt các module tham gia gồm `nhan_su`, `quan_ly_tai_san` và `account`.

## Mức 2 - Tự động hóa quy trình

Phiên bản hiện tại đã bổ sung các trigger tự động hóa để đáp ứng mức 2:

- Trigger theo lịch: cron hàng tháng tự động tính khấu hao và ghi nhận bút toán vào sổ cái.
- Trigger theo sự kiện cấp phát: khi cấp phát lại một tài sản, hệ thống tự động đóng phân bổ cũ đang hoạt động của tài sản đó.
- Trigger theo sự kiện HRM: khi nhân sự được điều chuyển phòng ban trong `lich_su_cong_tac`, hệ thống tự động thu hồi các phân bổ tài sản không còn hợp lệ với phòng ban mới.
    
