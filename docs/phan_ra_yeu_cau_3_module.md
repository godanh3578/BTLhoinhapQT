# Phan ra yeu cau de tai theo huong doanh nghiep

Tai lieu nay chinh lai pham vi de tai theo dung huong doanh nghiep.

## 1. Pham vi dung cua de tai

Ten de tai dang cho thay day la bai toan quan ly tai san cua cong ty, gan voi tai chinh va ke toan doanh nghiep, khong phai bai toan tai san ca nhan.

Trong pham vi nay:

1. Tai san la tai san thuoc doanh nghiep.
2. Khau hao la khau hao tai san co dinh cua doanh nghiep.
3. Gia tri tai san phai lien thong voi so sach ke toan.
4. Mua sam tai san phai lien quan den ngan sach, dong tien, phe duyet va chung tu.
5. Nhan su chi dong vai tro don vi su dung, nguoi quan ly, nguoi ban giao, nguoi phu trach tai san, khong phai trung tam cua de tai.

Phan truoc nghieng sang `tai san chung/rieng`, `the chap`, `nguoi dung ten` la huong gan voi boi canh ca nhan hoac phap ly so huu. Huong do khong sat voi ten de tai hien tai, nen khong nen de lam trong tam.

## 2. Dinh huong dung cua he thong

Neu di dung theo de tai, he thong nen tap trung vao 2 khoi chinh va 1 khoi ho tro:

1. `quan_ly_tai_san`
   - Quan ly danh muc tai san co dinh cua cong ty.
   - Ghi nhan nguyen gia, gia tri con lai, ngay mua, loai tai san.
   - Theo doi cap phat cho phong ban, nhan vien, dia diem su dung.
   - Theo doi lich su dieu chuyen, thu hoi, thanh ly.
   - Tu dong tinh khau hao hang thang.

2. `quan_ly_tai_chinh_ke_toan`
   - Quan ly de nghi mua sam, de nghi chi, nguon ngan sach.
   - Ghi nhan but toan ke toan lien quan den tai san.
   - Ghi nhan but toan khau hao vao so cai.
   - Theo doi dong tien va ngan sach mua sam tai san.
   - Bao cao tong hop cho bo phan tai chinh ke toan.

3. `nhan_su` hoac `don_vi_su_dung`
   - Chi la khoi ho tro de biet tai san dang giao cho ai, phong ban nao.
   - Khong nen dat lam trong tam neu ten de tai khong yeu cau quan ly nhan su.

## 3. Doi chieu voi code hien co

### Da co phan sat de tai

1. Da co module tai san.
   - Co model tai san va danh muc tai san.
   - Co nguyen gia, gia tri hien tai, ngay mua, loai tai san.
   - Co phan bo cho phong ban va nhan vien.

2. Da co khau hao tai san.
   - Co phuong phap khau hao.
   - Co lich su khau hao theo ky.
   - Co tao but toan ke toan khi khau hao.

3. Da co lien ket voi ke toan.
   - Loai tai san da co cau hinh tai khoan nguyen gia, tai khoan chi phi khau hao, tai khoan hao mon luy ke, so nhat ky khau hao.

### Chua sat de tai hoac chua du

1. Chua co module nghiep vu rieng cho `tai chinh/ke toan` o cap quy trinh.
   - Chua co de nghi mua sam.
   - Chua co de nghi chi cho mua tai san.
   - Chua co theo doi ngan sach mua sam.
   - Chua co theo doi nguon kinh phi.

2. Chua co quy trinh nghiep vu mua tai san tu dau den cuoi.
   - Nhu cau mua sam.
   - Phe duyet.
   - Ghi nhan chi.
   - Hinh thanh tai san.
   - Dua vao su dung.

3. Chua co bao cao quan tri tai chinh gan voi tai san.
   - Tong nguyen gia theo loai tai san.
   - Gia tri con lai theo phong ban.
   - Khau hao theo thang/quy/nam.
   - So sanh ngan sach va chi thuc te.

4. Module `quan_ly_van_ban` khong nam trong trong tam cua de tai hien tai.
   - Neu khong co yeu cau rieng tu giao vien, co the xem day la phan phu.

## 3.1. Yeu cau phu bat buoc: lien ket Nhan su va Quan ly van ban

Mac du `quan_ly_van_ban` khong phai trong tam cua de tai tai san - tai chinh - ke toan, day van la yeu cau phu bat buoc neu giao vien da giao rieng.

Muc tieu dung cua phan nay:

1. Tu ho so nhan vien xem duoc cac van ban lien quan.
2. Tu van ban biet ai xu ly, ai ky, ai nhan/phoi hop.
3. Cho phep di chuyen qua lai giua nghiep vu nhan su va nghiep vu van ban.

### Trang thai hien tai trong code

Phan nay thuc te da duoc lam trong module `quan_ly_van_ban`:

1. Tren model `van_ban_den` da co:
   - `nhan_vien_xu_ly_id`
   - `nhan_vien_ky_id`
   - `nhan_vien_nhan_ids`

2. Tren model mo rong `nhan_vien` da co:
   - `van_ban_den_xu_ly_ids`
   - `van_ban_den_ky_ids`
   - `van_ban_den_nhan_ids`
   - `van_ban_den_count`
   - `action_open_van_ban_den`

3. Tren giao dien nhan vien da co:
   - Smart button mo danh sach van ban
   - Tab van ban xu ly
   - Tab van ban ky
   - Tab van ban nhan/phoi hop

Tuc la ve chuc nang, lien ket Nhieu - Mot va Smart Button hien da dap ung huong dan giao vien.

### Dependency dung trong Odoo

Day la diem can chot lai cho dung.

Khong nen de:

1. `nhan_su` phu thuoc `quan_ly_van_ban`
2. Dong thoi `quan_ly_van_ban` lai phu thuoc `nhan_su`

Vi nhu vay se tao vong phu thuoc giua hai module.

Huong dung hien tai trong repo la hop ly:

1. `nhan_su` la module goc, chi phu thuoc `base`
2. `quan_ly_van_ban` phu thuoc `nhan_su`
3. Trong `quan_ly_van_ban`, model `nhan_vien` duoc mo rong bang `_inherit = 'nhan_vien'`

Neu muon tach sach hon nua, co the tao module cau noi rieng, vi du:

1. `nhan_su`
2. `quan_ly_van_ban`
3. `nhan_su_van_ban_bridge`

Khi do module cau noi se phu thuoc ca `nhan_su` va `quan_ly_van_ban`, con 2 module goc khong phu thuoc vong vao nhau.

### Ket luan cho yeu cau nay

1. Yeu cau lien ket Nhan su - Van ban la can co.
2. Code hien tai cua ban da co phan lon chuc nang nay.
3. Khong can doi `nhan_su` thanh `depends: ['base', 'quan_ly_van_ban']` trong cau truc hien tai.
4. Cach dung la giu `quan_ly_van_ban` phu thuoc `nhan_su`, vi toan bo phan mo rong dang nam trong module van ban.

## 4. Cach hieu dung cau mo ta de tai

Cau mo ta:

`Khau hao & Gia tri: Tu dong tinh toan khau hao tai san hang thang va ghi nhan vao so cai ke toan, giup quan ly dong tien va ngan sach mua sam.`

Nen duoc hieu thanh 4 nhom chuc nang doanh nghiep:

1. Quan ly tai san co dinh
   - Tao tai san.
   - Phan loai tai san.
   - Ghi nhan nguyen gia.
   - Ghi nhan gia tri con lai.

2. Khau hao
   - Chon phuong phap khau hao.
   - Tu dong chay khau hao hang thang.
   - Tao lich su khau hao.
   - Khong khau hao trung ky.

3. Ke toan
   - Tao but toan khau hao.
   - Day du tai khoan no/co.
   - Theo doi so nhat ky, but toan, doi soat `account.move`.

4. Tai chinh quan tri
   - Theo doi ngan sach mua sam.
   - Theo doi nguon kinh phi mua tai san.
   - Theo doi chi da thuc hien cho tai san.
   - So sanh ke hoach va thuc te.

Tuc la trong de tai nay, `Tai chinh` nghieng ve quan tri ngan sach va dong tien, con `Ke toan` nghieng ve ghi nhan so sach.

## 5. Mo hinh module nen chinh lai

Thay vi huong cu, nen chot lai nhu sau:

### Module 1: `quan_ly_tai_san`

Phu trach:

1. Danh muc tai san.
2. Tai san cu the.
3. Cap phat va thu hoi tai san.
4. Dieu chuyen tai san giua phong ban.
5. Thanh ly, hong hoc, ngung su dung.
6. Khau hao va lich su khau hao.

Model can co hoac can hoan thien:

1. `danh_muc_tai_san`
2. `tai_san`
3. `phan_bo_tai_san`
4. `lich_su_khau_hao`
5. `bien_dong_tai_san` hoac `lich_su_dieu_chuyen_tai_san`

Field nghiep vu nen co them o `tai_san`:

1. `ma_tai_san`
2. `ten_tai_san`
3. `ngay_mua_ts`
4. `ngay_ghi_tang`
5. `nguyen_gia`
6. `gia_tri_con_lai`
7. `gia_tri_thu_hoi_uoc_tinh`
8. `so_nam_khau_hao`
9. `bo_phan_su_dung_id`
10. `dia_diem_su_dung`
11. `trang_thai_tai_san`
12. `de_nghi_mua_sam_id`
13. `chung_tu_mua_sam_id`

### Module 2: `quan_ly_tai_chinh_ke_toan`

Phu trach:

1. De nghi mua sam tai san.
2. Theo doi ngan sach mua sam.
3. Theo doi nguon kinh phi.
4. De nghi chi va ghi nhan chi phi mua tai san.
5. Ghi nhan but toan tang tai san.
6. Ghi nhan but toan khau hao.
7. Bao cao dong tien lien quan tai san.

Model de xuat:

1. `ngan_sach_mua_sam`
   - `ma_ngan_sach`
   - `ten_ngan_sach`
   - `nam_ngan_sach`
   - `so_tien_duyet`
   - `so_tien_da_dung`
   - `so_tien_con_lai`
   - `trang_thai`

2. `nguon_kinh_phi`
   - `ma_nguon`
   - `ten_nguon`
   - `loai_nguon`
   - `ghi_chu`

3. `de_nghi_mua_sam`
   - `so_de_nghi`
   - `ngay_de_nghi`
   - `phong_ban_id`
   - `nguoi_de_nghi_id`
   - `noi_dung_mua_sam`
   - `du_toan_chi_phi`
   - `ngan_sach_id`
   - `nguon_kinh_phi_id`
   - `trang_thai`

4. `de_nghi_mua_sam_line`
   - `de_nghi_mua_sam_id`
   - `ten_hang_muc`
   - `so_luong`
   - `don_gia_du_kien`
   - `thanh_tien_du_kien`
   - `co_hinh_thanh_tai_san`

5. `chung_tu_mua_tai_san`
   - `so_chung_tu`
   - `ngay_chung_tu`
   - `doi_tac`
   - `gia_tri_thanh_toan`
   - `de_nghi_mua_sam_id`
   - `account_move_id`

6. `phe_duyet_nghiep_vu`
   - `ref_model`
   - `ref_id`
   - `cap_duyet`
   - `nguoi_duyet_id`
   - `ngay_duyet`
   - `ket_qua`
   - `y_kien`

Ghi chu:

- Neu muon gon, co the khong tach module `tai_chinh` va `ke_toan` thanh 2 module rieng.
- Co the gom lai thanh 1 module `quan_ly_tai_chinh_ke_toan` va dung module Odoo `account` lam tang ha tang so sach.

### Module 3: `nhan_su` hoac `don_vi_su_dung`

Day la module ho tro, khong phai trong tam.

Phu trach:

1. Quan ly phong ban.
2. Quan ly nhan vien nhan ban giao tai san.
3. Xac dinh bo phan dang su dung tai san.

Neu muon sat de tai hon nua, thuc te co the khong can mo rong `nhan_su`, chi can du lieu `phong_ban`, `nguoi_nhan_ban_giao` la du.

## 6. Bang phan ra yeu cau theo huong doanh nghiep

| Yeu cau de tai | Hien trang | Can lam them |
| --- | --- | --- |
| Quan ly tai san doanh nghiep | Da co khung | Bo sung ngay ghi tang, thanh ly, dieu chuyen, lich su bien dong |
| Tu dong tinh khau hao hang thang | Da co mot phan | Hoan thien kiem soat ky khau hao, cron, bao cao tong hop |
| Ghi nhan vao so cai ke toan | Da co mot phan | Hoan thien quy trinh doi soat but toan va lien ket chung tu goc |
| Quan ly dong tien mua sam | Chua co | Them ngan sach, nguon kinh phi, de nghi mua sam, chung tu mua |
| Quan ly ngan sach mua sam | Chua co | Them model ngan sach va bao cao so sanh duyet/thuc te |
| Theo doi phong ban su dung tai san | Da co | Hoan thien bien dong cap phat, dieu chuyen, thu hoi |
| Bao cao gia tri tai san theo thoi gian | Chua du | Them dashboard va bao cao theo thang, quy, nam |

## 7. Menu nen co

### `quan_ly_tai_san`

1. Danh muc tai san
2. Tai san
3. Cap phat tai san
4. Dieu chuyen tai san
5. Thanh ly tai san
6. Lich su khau hao
7. Bao cao tai san

### `quan_ly_tai_chinh_ke_toan`

1. Ngan sach mua sam
2. Nguon kinh phi
3. De nghi mua sam
4. Chung tu mua tai san
5. Phe duyet
6. But toan tai san
7. Bao cao dong tien
8. Bao cao ngan sach

### `nhan_su` ho tro

1. Phong ban
2. Nhan vien
3. Ban giao tai san

## 8. Nhom quyen nen co

1. `group_asset_user`
   - Quan ly danh muc va ho so tai san.

2. `group_asset_manager`
   - Cap phat, dieu chuyen, thanh ly tai san.

3. `group_finance_user`
   - Lap de nghi mua sam, theo doi ngan sach.

4. `group_finance_manager`
   - Duyet de nghi, kiem soat nguon kinh phi.

5. `group_accountant`
   - Ghi nhan but toan tang tai san va khau hao.

6. `group_auditor_viewer`
   - Xem bao cao va lich su doi soat.

## 9. Workflow dung va sat de tai

### Quy trinh mua sam tai san

1. Phong ban lap `de_nghi_mua_sam`.
2. Bo phan tai chinh kiem tra ngan sach va nguon kinh phi.
3. Cap co tham quyen phe duyet.
4. Sau khi mua xong, tao `chung_tu_mua_tai_san`.
5. He thong ghi nhan `tai_san` moi.
6. Ke toan ghi but toan tang tai san.
7. Dua tai san vao su dung va cap phat cho phong ban.

### Quy trinh khau hao hang thang

1. He thong cron chay theo ky.
2. Tinh so tien khau hao.
3. Tao `lich_su_khau_hao`.
4. Tao `account.move`.
5. Cap nhat gia tri con lai cua tai san.
6. Dua vao bao cao khau hao va bao cao gia tri tai san.

## 10. Ket luan da chinh lai

Huong dung cua de tai la:

1. Tai san cua cong ty.
2. Khau hao theo chuan quan ly tai san doanh nghiep.
3. Ghi nhan ke toan vao so cai.
4. Theo doi dong tien va ngan sach mua sam.

Vi vay:

1. `tai san chung/rieng`, `the chap`, `nguoi dung ten` khong nen de lam trong tam nua.
2. Trong tam nen doi sang `mua sam`, `ngan sach`, `nguon kinh phi`, `ghi tang tai san`, `khau hao`, `but toan`, `bao cao`.
3. `nhan_su` chi nen giu vai tro phu tro cho viec ban giao va su dung tai san.

## 11. Huong trien khai tiep theo

Neu di tiep theo huong nay, thu tu hop ly nhat la:

1. Hoan thien `quan_ly_tai_san` theo huong doanh nghiep.
2. Tao module moi `quan_ly_tai_chinh_ke_toan`.
3. Noi quy trinh `de_nghi_mua_sam -> chung_tu_mua -> tao tai_san -> khau_hao -> but_toan`.
4. Sau cung moi lam bao cao va dashboard.