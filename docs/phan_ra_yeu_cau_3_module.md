# Phân rã yêu cầu đề tài theo hướng doanh nghiệp

## 1. Phạm vi đề tài

Đề tài được chốt theo ba khối nghiệp vụ tích hợp trên Odoo 15:

1. `nhan_su`
2. `quan_ly_tai_san`
3. `quan_ly_tai_chinh_ke_toan`

Trọng tâm của bài là quản lý tài sản doanh nghiệp gắn với quản trị tài chính và ghi nhận kế toán. HRM đóng vai trò dữ liệu gốc để xác định phòng ban, nhân sự sử dụng tài sản và luồng điều chuyển nội bộ.

## 2. Vai trò của từng module

### 2.1. Module `nhan_su`

Chức năng chính:

1. Quản lý hồ sơ nhân viên
2. Quản lý phòng ban và chức vụ
3. Quản lý lịch sử công tác
4. Xác định phòng ban hiện tại của nhân viên để làm dữ liệu nguồn cho tài sản và tài chính

Giá trị trong hệ thống tích hợp:

1. Tránh nhập lại thông tin nhân sự ở các module khác
2. Đảm bảo tài sản được phân bổ đúng người, đúng phòng ban
3. Cung cấp trigger nghiệp vụ khi nhân sự điều chuyển

### 2.2. Module `quan_ly_tai_san`

Chức năng chính:

1. Quản lý danh mục tài sản
2. Quản lý từng tài sản cụ thể
3. Phân bổ tài sản cho phòng ban và nhân viên
4. Thu hồi hoặc đóng phân bổ khi có thay đổi sử dụng
5. Tính khấu hao hàng tháng
6. Ghi nhận lịch sử khấu hao và liên kết bút toán kế toán

Giá trị trong hệ thống tích hợp:

1. Truy vết tài sản đang do ai sử dụng
2. Theo dõi giá trị còn lại của tài sản theo thời gian
3. Tự động chuyển chi phí khấu hao sang sổ cái kế toán

### 2.3. Module `quan_ly_tai_chinh_ke_toan`

Chức năng chính:

1. Quản lý ngân sách mua sắm
2. Quản lý nguồn kinh phí
3. Quản lý đề nghị mua sắm tài sản
4. Quản lý chứng từ mua tài sản
5. Tự động tạo bút toán mua sắm tài sản
6. Tự động sinh tài sản từ các hạng mục mua sắm hợp lệ
7. Phân tích đề nghị mua sắm bằng AI
8. Gửi thông báo Telegram qua External API

Giá trị trong hệ thống tích hợp:

1. Kết nối luồng ngân sách, mua sắm và hình thành tài sản
2. Hỗ trợ tài chính kiểm soát dòng tiền mua sắm
3. Tăng tốc xử lý nghiệp vụ bằng AI và API ngoài

## 3. Phân rã yêu cầu theo rubric

### 3.1. Mức 1 - Tích hợp hệ thống

Yêu cầu:

1. Các module dùng chung một cơ sở dữ liệu
2. HRM là dữ liệu gốc để đồng bộ sang các module khác
3. Không nhập trùng dữ liệu nhân sự

Hiện trạng đáp ứng:

1. `quan_ly_tai_san` phụ thuộc `nhan_su` và `account`
2. `quan_ly_tai_chinh_ke_toan` phụ thuộc `nhan_su`, `quan_ly_tai_san`, `account`
3. Đề nghị mua sắm và phân bổ tài sản lấy dữ liệu từ nhân viên, phòng ban hiện có trong HRM

Kết luận:

Mức 1 đạt.

### 3.2. Mức 2 - Tự động hóa quy trình

Yêu cầu:

1. Hệ thống phải tự động chạy tác vụ theo lịch hoặc theo sự kiện
2. Giảm thao tác thủ công trong luồng nghiệp vụ

Hiện trạng đáp ứng:

1. Cron hàng tháng tự tính khấu hao và tạo bút toán kế toán
2. Khi tài sản được cấp phát lại, hệ thống tự động đóng phân bổ cũ
3. Khi HR điều chuyển nhân sự, hệ thống tự động thu hồi các phân bổ không còn hợp lệ
4. Khi ghi nhận chứng từ mua tài sản, hệ thống tự động tạo bút toán kế toán mua sắm
5. Khi ghi nhận chứng từ mua tài sản, hệ thống tự động sinh tài sản từ các hạng mục hình thành tài sản

Kết luận:

Mức 2 đạt.

### 3.3. Mức 3 - AI và External API

Yêu cầu:

1. Tích hợp AI hoặc LLM để xử lý một vấn đề nghiệp vụ trong module
2. Tích hợp External API với nền tảng ngoài hệ thống

Hiện trạng đáp ứng:

1. AI/LLM được dùng để phân tích đề nghị mua sắm bằng OpenAI hoặc Gemini
2. Kết quả AI hỗ trợ đánh giá nhu cầu, rủi ro ngân sách và gợi ý xử lý
3. External API Telegram được dùng để gửi thông báo khi đề nghị được phê duyệt
4. External API Telegram được dùng để gửi thông báo khi chứng từ mua tài sản được ghi nhận

Kết luận:

Mức 3 đạt nếu môi trường triển khai đã cấu hình API key AI và Telegram bot token hợp lệ.

## 4. Điều kiện triển khai thực tế

Để bài chạy ổn định khi bảo vệ hoặc nộp sản phẩm, cần chuẩn bị:

1. Cài đủ ba module `nhan_su`, `quan_ly_tai_san`, `quan_ly_tai_chinh_ke_toan`
2. Cấu hình chart of accounts trong Odoo
3. Cấu hình journal và account cho loại tài sản, nguồn kinh phí
4. Cấu hình API key OpenAI hoặc Gemini nếu dùng AI
5. Cấu hình bot token và chat id nếu dùng Telegram

## 5. Artifact nộp bài

Các artifact hiện đã đồng bộ theo tên nhóm `Nhom6`:

1. Business flow: `docs/business flow/Nhom6_BusinessFlow_QuanLyTaiSanKeToanHRM.png`
2. Poster: `docs/poster/Nhom6_Poster_QuanLyTaiSanKeToanHRM.png`
3. Mã nguồn trên GitHub
4. README mô tả hệ thống

## 6. Kết luận

Bài được định hình theo hướng doanh nghiệp, có đủ ba lớp:

1. Tích hợp dữ liệu gốc từ HRM
2. Tự động hóa quy trình tài sản và tài chính
3. Ứng dụng AI và External API trong nghiệp vụ thực tế

Với trạng thái mã nguồn hiện tại, bài phù hợp với mục tiêu đạt Mức 1, Mức 2 và Mức 3 của rubric, với điều kiện triển khai đúng cấu hình vận hành.
 