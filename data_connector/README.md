# Data Connectors (Proof of Concept)

Thư mục này chứa các mã nguồn Python thực tế dùng để chứng minh tính khả thi của việc kết nối và tự động lấy dữ liệu từ các Enterprise Apps (SharePoint, SAP) nhằm mục đích đưa vào Knowledge Base (ChromaDB) của RAG.

## 1. SharePoint / OneDrive Connector (`sharepoint_connector.py`)

Kịch bản này sử dụng thư viện `msal` và `Microsoft Graph API` để quét và tải file từ thư mục đám mây của Microsoft. Logic xác thực OAuth2 (Device Flow) được tái sử dụng trực tiếp từ script Outlook cũ của bạn.

### Cách tạo thư mục để test
Rất đơn giản, bạn KHÔNG cần phải thiết lập một hệ thống SharePoint Admin cồng kềnh. Script này được thiết kế để quét thư mục gốc (`root`) của tài khoản Microsoft bạn dùng để đăng nhập.
1. Bạn đăng nhập vào [OneDrive](https://onedrive.live.com) (tài khoản cá nhân hoặc công ty đều được).
2. Tạo một vài file PDF, Word hoặc TXT ở ngay thư mục gốc (Root).
3. Chạy lệnh: `python3 sharepoint_connector.py`
4. Cửa sổ dòng lệnh sẽ văng ra một mã Code. Bạn vào `https://microsoft.com/devicelogin`, nhập mã Code đó và đăng nhập bằng tài khoản OneDrive của bạn.
5. Code sẽ tự động quét thư mục OneDrive/SharePoint của bạn, tìm các file tài liệu và mô phỏng việc tải về thư mục `downloaded_docs`.

## 2. SAP ERP Connector (`sap_connector.py`)

Kịch bản này sử dụng chuẩn REST API **OData** - đây là "ngôn ngữ chung" của 99% các hệ thống SAP S/4HANA và SAP ECC hiện đại (thông qua SAP Gateway).

### Cách hoạt động
Thay vì bạn phải cài đặt một hệ thống SAP S/4HANA nặng hàng trăm GB, script này được trỏ thẳng tới **OData V4 Reference Service (TripPin)** của OData.org. Hệ thống này có cấu trúc API JSON giống hệt 100% so với một API OData của SAP.
1. Chạy lệnh: `python3 sap_connector.py`
2. Script sẽ gọi API, lấy về các bản ghi JSON có cấu trúc.
3. Kỹ thuật quan trọng nhất trong script này là: **Biến đổi JSON thành Natural Language (Văn bản tự nhiên)**. VectorDB và LLM không giỏi đọc JSON thô, nên script đã ghép các trường (Tên, Họ, Email) thành một đoạn văn hoàn chỉnh để chuẩn bị nạp vào RAG.

## Bước tiếp theo (Sync Engine)

Sau khi bạn chạy thử 2 file này và thấy dữ liệu "chảy" về máy thành công, bước tiếp theo chúng ta sẽ viết `sync_engine.py` để tự động hóa việc gọi 2 script này mỗi 5 phút, sau đó lấy kết quả nạp thẳng vào ChromaDB.
