# Kịch bản Kiểm thử Tích hợp Toàn diện (Môi trường N1)

Tài liệu này hướng dẫn cách test toàn bộ luồng tích hợp, bao gồm cả trường hợp lỗi Firewall (Không kết nối được) và sự khác biệt giữa việc test bằng Data Thật (Real Data) vs Data Giả lập (Mock Data).

---

## Tình huống 1: Mạng lưới và Firewall (N1 AWS -> PowerBI/Athena)
Hệ thống N1 chạy trên AWS cần phải ra ngoài Internet để gọi API.

*   **Rủi ro:** Firewall Outbound trên AWS N1 chặn kết nối đến Microsoft (`api.powerbi.com` / `login.microsoftonline.com`).
*   **Cách kiểm tra (Test Connection - Không kết nối được):**
    *   Chạy script `firewall_test.js` (đã được cấp kèm trong bộ Demo).
    *   **Kết quả Pass:** Script báo "Connected successfully" tới Microsoft.
    *   **Kết quả Lỗi (Firewall block):** Script báo "Timeout" hoặc "ECONNREFUSED". Nếu gặp lỗi này, bắt buộc phải chuyển sang **Approach 2 (Dùng Athena + ChartJS)** hoặc yêu cầu NetOps mở port.

## Tình huống 2: Xác thực & API (Test Mock Data vs Real Data)
Server MCP cần lấy dữ liệu hoặc Token.

*   **Cách kiểm tra (Test Mock Data):**
    *   Cố tình KHÔNG điền file `.env` (để trống Client ID/Secret).
    *   Bật MCP Server lên. Server sẽ tự động rơi vào chế độ Mock.
    *   Gọi thử lệnh DAX hoặc Athena. Server sẽ trả về một file JSON giả (Ví dụ: `{"mock": true, "data": [...]}`). Việc này giúp Frontend team có thể code UI ngay lập tức mà không cần chờ team BI.
*   **Cách kiểm tra (Test Real Data):**
    *   Điền ID/Secret thật vào `.env`.
    *   Gọi MCP Server. Nếu trả về lỗi 401/403 -> Sai quyền. Nếu trả về JSON chứa data thật của công ty -> Cấu hình hoàn hảo.

## Tình huống 3: UI Tương tác (Interactive ChartJS & PowerBI)
Viết code Frontend hiển thị biểu đồ.

*   **Cách kiểm tra (PowerBI Iframe):** 
    *   Truyền thử một Embed Token (mock hoặc real) vào Frontend. Nếu trắng màn hình, check lại CSP (Content Security Policy).
*   **Cách kiểm tra (ChartJS - Approach 2):**
    *   Mở file `index.html` của phần Demo ChartJS.
    *   Nhập Mock JSON vào và bấm Render. Đưa chuột qua các cột xem Tooltip có hiển thị không (Interactive).

## Tình huống 4: Tính năng Drill-down (Click để xem chi tiết)
Khi user click vào cột "Năm 2023", hiển thị bảng Data Table của 12 tháng năm 2023.

*   **Rủi ro:** Luồng bắt sự kiện click (onclick) không truyền đúng tham số đi.
*   **Cách kiểm tra:**
    *   Trong bảng Demo ChartJS, bật chế độ "Raw Data JSON".
    *   Click vào thanh biểu đồ (Bar). 
    *   **Kết quả Pass:** UI tự động bắt sự kiện, ẩn biểu đồ Bar đi và hiện ra một Data Table (bảng HTML) chứa dữ liệu chi tiết của cột vừa click.

## Tình huống 5: Sự thông minh của AI
*   **Cách kiểm tra:** Nhập câu hỏi "Doanh thu năm 2023 là bao nhiêu". Xem AI sinh ra chuỗi DAX (Approach 1) hoặc SQL (Approach 2) có đúng bảng/cột không.
