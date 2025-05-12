# KeyFindingApp

## Tổng quan

**KeyFindingApp** là một ứng dụng desktop dựa trên Python được thiết kế để hỗ trợ phân tích lược đồ cơ sở dữ liệu quan hệ. Ứng dụng giúp người dùng tìm tập đóng của các thuộc tính (X⁺), các khóa ứng viên (K1, K2, K3, KS1, KS2, KS3, KS4, KS5, KS6), và tập phụ thuộc hàm tối thiểu (F1, F2, F3).  
Ứng dụng có giao diện người dùng đồ họa (GUI) được xây dựng bằng **Tkinter** và hỗ trợ lưu kết quả vào cơ sở dữ liệu **SQL Server** để theo dõi lịch sử.

---

## Tính năng

- **Tìm X⁺**: Tính tập đóng của một tập thuộc tính dựa trên các phụ thuộc hàm đã cho.
- **Tìm khóa**: Xác định các khóa ứng viên bằng nhiều thuật toán (K1, K2, K3, và KS1, KS2, KS3, KS4, KS5, KS6).
- **Tập tối thiểu**: Tính tập phụ thuộc hàm tối thiểu (F1, F2, F3).
- **Tích hợp cơ sở dữ liệu**: Lưu và truy xuất kết quả từ cơ sở dữ liệu SQL Server.
- **Theo dõi lịch sử**: Xem các phép tính trước đây, xuất ra file CSV, và xóa bản ghi nếu cần.

---

## Yêu cầu trước khi sử dụng

Trước khi chạy ứng dụng, hãy đảm bảo bạn đã cài đặt:

- **Python 3.6 trở lên**
- Các gói Python cần thiết:
  ```bash
  pip install pyodbc
  ```

- **SQL Server** (cục bộ hoặc từ xa) với thông tin đăng nhập:
  - Máy chủ: `.` (localhost) hoặc tên máy chủ của bạn
  - Cơ sở dữ liệu: `KeyFindingApp`
  - Tên người dùng: `sa`
  - Mật khẩu: `12345`

- **Trình điều khiển ODBC cho SQL Server** (kiểm tra bằng `check_driver.py`)

---

## Cài đặt

1. **Sao chép kho lưu trữ về máy cục bộ:**
   ```bash
   git clone https://github.com/your-username/KeyFindingApp.git
   ```

2. **Điều hướng đến thư mục dự án:**
   ```bash
   cd KeyFindingApp
   ```

3. **Cài đặt các phụ thuộc cần thiết:**
   ```bash
   pip install pyodbc
   ```

4. **Đảm bảo SQL Server đang chạy và được cấu hình với cơ sở dữ liệu `KeyFindingApp`.**

---

## Hướng dẫn sử dụng

- **Chạy ứng dụng:**
  ```bash
  python main.py
  ```

- Giao diện GUI sẽ mở ra với các tab:
  - **Tìm X⁺**: Nhập tập phổ quát `U`, các phụ thuộc hàm `F`, và một tập `X` để tính tập đóng.
  - **Tìm khóa**: Tính các khóa ứng viên bằng các thuật toán (K1, K2, K3, KS1, KS2, KS3, KS4, KS5, KS6).
  - **Tìm Fc**: Tính tập phụ thuộc hàm tối thiểu (F1, F2, F3).

- **Cách sử dụng:**
  - Nhập tập phổ quát `U` (ví dụ: `ABCDEF`) và thêm các phụ thuộc hàm (ví dụ: `AB -> CD`).
  - Sử dụng các nút tương ứng để tính `X⁺`, khóa, hoặc tập tối thiểu.
  - Lưu kết quả vào SQL Server bằng nút **"Lưu vào SQL Server"**.
  - Xem kết quả trước đó qua menu **"Công cụ → Xem lịch sử"**, nơi bạn có thể xuất CSV hoặc xóa bản ghi.

---

## Cấu trúc tệp

- `check_driver.py`: Kiểm tra trình điều khiển ODBC có sẵn trên hệ thống.
- `db.py`: Xử lý kết nối DB, tạo bảng, thao tác CRUD với SQL Server.
- `fc_generator.py`: Triển khai thuật toán tìm tập phụ thuộc hàm tối thiểu (F1, F2, F3).
- `key_finder.py`: Thuật toán tìm khóa ứng viên (K1, K2, K3, KS1, KS2, KS3, KS4, KS5, KS6).
- `utils.py`: Các hàm tiện ích xử lý chuỗi và tập hợp.
- `x_plus.py`: Tính tập đóng của một tập thuộc tính (X⁺).
- `main.py`: Chạy giao diện người dùng Tkinter chính.

---

## Lược đồ cơ sở dữ liệu

Ứng dụng sử dụng ba bảng trong cơ sở dữ liệu **KeyFindingApp**:

1. **RelationalSchemaLogs**: Lưu đầu vào và kết quả X⁺.
2. **KeyFindingLogs**: Lưu các khóa đã tính (K1, K2, K3, KS1,KS2, KS3, KS4, KS5, KS6).
3. **MinimalCoverLogs**: Lưu các tập phụ thuộc hàm tối thiểu (F1, F2, F3).

Mỗi bảng có các cột: `ID`, `U`, `f_list`, các trường kết quả tương ứng, và `created_at`.

---

## Khắc phục sự cố

- **Vấn đề kết nối DB**: Đảm bảo SQL Server đang chạy và thông tin đăng nhập đúng (`db.py`). Kiểm tra driver bằng `check_driver.py`.
- **Thiếu phụ thuộc**: Chạy lệnh:
  ```bash
  pip install pyodbc
  ```
- **Lỗi GUI**: Đảm bảo Tkinter đã cài đặt (có sẵn trong cài đặt chuẩn của Python).

---

## Lời cảm ơn

Ứng dụng này được phát triển nhằm hỗ trợ học tập và hiểu sâu hơn về các khái niệm **cơ sở dữ liệu quan hệ**, như **phụ thuộc hàm** và **khóa ứng viên**.
