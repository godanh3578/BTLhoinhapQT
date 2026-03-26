# Phân tích nghiệp vụ tích hợp HRM - Quản lý tài sản - Tài chính/Kế toán

## 1. Phạm vi đề tài

Đề tài tập trung vào ba trục nghiệp vụ dùng chung một cơ sở dữ liệu trên Odoo 15:

- `nhan_su`: dữ liệu gốc về nhân viên, phòng ban, chức vụ và lịch sử công tác.
- `quan_ly_tai_san`: quản lý danh mục tài sản, phân bổ tài sản, theo dõi người sử dụng và lịch sử khấu hao.
- `account`: ghi nhận bút toán khấu hao vào sổ cái kế toán, phục vụ báo cáo chi phí và kiểm soát ngân sách.

## 2. Phân tích nghiệp vụ từng module

### 2.1. Module HRM (`nhan_su`)

Vai trò:

- Là nguồn dữ liệu gốc cho nhân viên và phòng ban.
- Quản lý lịch sử công tác để xác định nhân viên đang thuộc phòng ban nào tại một thời điểm.
- Cung cấp dữ liệu đồng bộ cho module tài sản mà không nhập lại tay.

Nghiệp vụ chính:

- Tạo hồ sơ nhân viên với mã định danh duy nhất.
- Theo dõi lịch sử điều chuyển phòng ban, chức vụ.
- Xác định phòng ban hiện tại của nhân viên làm căn cứ phân bổ tài sản.

### 2.2. Module Quản lý tài sản (`quan_ly_tai_san`)

Vai trò:

- Quản lý hồ sơ tài sản, loại tài sản, giá trị ban đầu, giá trị còn lại.
- Quản lý việc phân bổ tài sản cho phòng ban hoặc nhân viên cụ thể.
- Tính khấu hao theo tháng và lưu lịch sử khấu hao.

Nghiệp vụ chính:

- Khai báo tài sản mới theo danh mục tài sản.
- Cấu hình phương pháp khấu hao, chu kỳ khấu hao và ngày bắt đầu khấu hao.
- Phân bổ tài sản cho đúng phòng ban và đúng nhân viên đang thuộc phòng ban đó.
- Theo dõi trạng thái tài sản: chưa phân bổ, đang sử dụng, đã khấu hao hết.

### 2.3. Module Kế toán/Tài chính (`account`)

Vai trò:

- Ghi nhận chi phí khấu hao vào sổ cái.
- Theo dõi hao mòn lũy kế và nguyên giá theo từng loại tài sản.
- Hỗ trợ bộ phận tài chính kiểm soát chi phí và lập kế hoạch ngân sách mua sắm.

Nghiệp vụ chính:

- Cấu hình nhật ký khấu hao.
- Cấu hình tài khoản chi phí khấu hao, tài khoản hao mòn lũy kế, tài khoản nguyên giá.
- Tự động tạo bút toán kế toán khi tài sản đến kỳ khấu hao.

## 3. Nghiệp vụ tích hợp giữa các module

Luồng tích hợp chính:

1. HR tạo hoặc cập nhật hồ sơ nhân viên, phòng ban và lịch sử công tác.
2. Bộ phận tài sản tạo hồ sơ tài sản, cấu hình loại tài sản và thông số khấu hao.
3. Khi phân bổ tài sản, hệ thống bắt buộc chọn nhân viên từ dữ liệu HRM.
4. Hệ thống kiểm tra nhân viên có thuộc đúng phòng ban tại ngày phân bổ hay không.
5. Đến kỳ khấu hao, hệ thống tự động tạo lịch sử khấu hao cho tài sản.
6. Đồng thời hệ thống sinh bút toán hạch toán Nợ chi phí khấu hao/Có hao mòn lũy kế.
7. Sổ cái kế toán và giá trị còn lại của tài sản được cập nhật đồng nhất.

Giá trị tích hợp:

- Không nhập trùng dữ liệu nhân sự ở module tài sản.
- Truy vết được tài sản đang do ai sử dụng và thuộc phòng ban nào.
- Dòng tiền chi phí khấu hao được phản ánh tự động trong kế toán.

## 4. Hiện trạng triển khai

Phạm vi đã triển khai:

- Đã có hai module tùy biến `nhan_su` và `quan_ly_tai_san`.
- `quan_ly_tai_san` đã phụ thuộc trực tiếp vào `account` và `nhan_su`.
- Đã có lịch `cron` tính khấu hao hàng tháng.
- Đã có cấu hình tài khoản kế toán trên loại tài sản.
- Đã có ràng buộc kiểm tra nhân viên phải thuộc đúng phòng ban khi nhận tài sản.
- Đã có module `quan_ly_tai_chinh_ke_toan` cho ngân sách, nguồn vốn, đề nghị mua sắm và chứng từ.
- Đã có AI phân tích đề nghị mua sắm và tích hợp Telegram để gửi thông báo nghiệp vụ.

Điều kiện cần chuẩn bị khi triển khai và bảo vệ:

- Cần cấu hình đầy đủ journal, tài khoản nguồn vốn và API key trước khi vận hành các tính năng mới.
- Cần chuẩn bị tài khoản OpenAI hoặc Gemini và bot Telegram thật để chứng minh mức 3 khi bảo vệ.
- Poster và business flow đã được chuẩn hóa theo tên nhóm `Nhom6`.

## 5. Khoảng cần hoàn thiện

Phần đã hoàn thành:

- Dữ liệu nhân sự gốc.
- Quản lý danh mục, hồ sơ và phân bổ tài sản.
- Tự động tạo bút toán khấu hao hàng tháng.

Phần cần hoàn thiện thêm ngoài mã nguồn:

- Chuẩn hóa cấu hình triển khai để AI và Telegram chạy ổn định trên môi trường bảo vệ.
- Hoàn thiện artifact nộp bài bằng cách đổi tên poster, business flow, bổ sung video giới thiệu.

## 6. Phương án triển khai

- Giữ `nhan_su` là nguồn master data cho nhân viên/phòng ban.
- Duy trì `cron` khấu hao hàng tháng như tác vụ tự động hóa mức 2.
- Bổ sung trigger tự động đóng phân bổ cũ khi tài sản được cấp phát lại.
- Bổ sung trigger tự động thu hồi phân bổ tài sản không còn hợp lệ khi HR điều chuyển nhân sự sang phòng ban mới.
- Bổ sung tự động tạo bút toán mua tài sản và tự động hình thành tài sản từ chứng từ mua sắm.
- Bổ sung AI phân tích đề nghị mua sắm và Telegram notification như năng lực mức 3.
- Bổ sung tài liệu phân tích nghiệp vụ, ảnh business flow và poster giới thiệu hệ thống.

## 7. Mức độ đáp ứng theo rubric

- Mức 1: đạt yêu cầu tích hợp hệ thống vì ba module dùng chung cơ sở dữ liệu và HRM là dữ liệu gốc.
- Mức 2: đạt yêu cầu tự động hóa ở cả trigger theo lịch lẫn trigger theo sự kiện và tự động hóa tài chính.
- Trigger theo lịch: `cron` khấu hao hàng tháng tự động tạo lịch sử khấu hao và bút toán kế toán.
- Trigger theo sự kiện: khi tài sản được cấp phát lại, hệ thống tự động đóng phân bổ cũ; khi HR điều chuyển nhân sự sang phòng ban mới, hệ thống tự động thu hồi các phân bổ tài sản không còn hợp lệ.
- Trigger theo quy trình tài chính: khi chứng từ mua tài sản được ghi nhận, hệ thống tự động tạo bút toán kế toán và sinh tài sản từ các hạng mục hợp lệ.
- Mức 3: đã triển khai AI/LLM để phân tích đề nghị mua sắm và External API Telegram để gửi thông báo phê duyệt, ghi nhận chứng từ.