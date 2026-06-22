# Danh sách Yêu cầu & Cấu hình Tích hợp (PowerBI & Athena)

Tài liệu này dùng để gửi cho đội ngũ quản trị hệ thống / Data / BI để xin cấp quyền và cung cấp thông tin. Hệ thống Chatbot của chúng tôi có 2 hướng tiếp cận (Approach), vui lòng cung cấp thông tin cho cả 2 để chúng tôi có phương án dự phòng (Fallback) nếu hệ thống mạng N1 bị block.

---

## Phần 1: Dành cho Hướng tiếp cận PowerBI (Mạng thông suốt)
*Chatbot sẽ ưu tiên gọi PowerBI để lấy Embed Token (nhúng Iframe) hoặc lấy Raw JSON (cho drill-down).*

### 1. Thiết lập Xác thực (Azure AD)
- [ ] Tạo một **App Registration** (Service Principal) trên hệ thống Azure AD.
- [ ] Cung cấp 3 thông số: **`Tenant ID`**, **`Client ID`**, **`Client Secret`**.
- [ ] Trong PowerBI Admin Portal, bật **"Allow service principals to use Power BI APIs"**.
- [ ] Cấp quyền API Permission cho App: `Report.Read.All`, `Workspace.Read.All` và `Dataset.Read.All`.

### 2. Thông tương Workspace & Report (Dành cho việc Nhúng Iframe)
- [ ] **`Workspace ID`** (Phải thuộc Premium/Embedded Capacity).
- [ ] Add Service Principal vào Workspace với quyền **Member** hoặc **Admin**.
- [ ] Cung cấp danh sách **`Report ID`** được phép nhúng.
- [ ] Cung cấp danh sách **Table / Column** để làm cấu hình Filter.

### 3. Thông tin Data Schema (Dành cho việc gọi Data JSON thô / Drill-down)
*Nếu App click drill-down và cần data thô thay vì Iframe:*
- [ ] Cung cấp **`Dataset ID`** (Semantic Model ID).
- [ ] Cung cấp Data Dictionary (Danh sách Tables, Columns, Measures) để AI tự viết DAX Queries.

---

## Phần 2: Dành cho Hướng tiếp cận Athena (Dự phòng khi bị Firewall chặn)
*Nếu AWS N1 không thể gọi được PowerBI, Chatbot sẽ trực tiếp truy vấn Data Lake bằng SQL và tự render biểu đồ bằng ChartJS.*

### 1. Thiết lập Xác thực (AWS IAM)
- [ ] Tạo một IAM User hoặc Role cho Chatbot.
- [ ] Cung cấp **`AWS Access Key`** và **`AWS Secret Key`**.
- [ ] Cấp quyền IAM để Role này có thể thực thi `athena:StartQueryExecution` và `s3:GetObject` trên bucket chứa kết quả Athena.

### 2. Thông tin Data Schema (Dành cho AI viết lệnh SQL)
- [ ] Cung cấp danh sách các Bảng (Tables) có sẵn trên **Glue Catalog** (Database Name, Table Names).
- [ ] Tài liệu mô tả ý nghĩa các cột (Data Dictionary) để AI hiểu và viết đúng câu lệnh `SELECT`.
