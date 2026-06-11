import requests
import json
from datetime import datetime

# --- CẤU HÌNH API ODATA (SAP GIẢ LẬP) ---
# Trong thực tế, URL này sẽ là: https://<sap-host>/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder
# Ở đây ta dùng Northwind OData (chuẩn giống hệt SAP OData) để test
SAP_ODATA_URL = "https://services.odata.org/V4/TripPinServiceRW/People"

# --- TÍNH NĂNG CONNECTOR ---
def fetch_sap_data():
    print(f"\n[*] Đang kết nối tới hệ thống SAP (OData API) tại: {SAP_ODATA_URL} ...")
    
    try:
        # Trong thực tế, bạn sẽ cần truyền auth=(username, password)
        response = requests.get(SAP_ODATA_URL)
        response.raise_for_status()
        
        data = response.json()
        records = data.get("value", [])
        print(f"[+] Lấy thành công {len(records)} bản ghi từ SAP.\n")
        
        extracted_texts = []
        
        # Xử lý 3 bản ghi đầu tiên làm ví dụ
        for i, record in enumerate(records[:3]):
            # Trích xuất dữ liệu thô
            username = record.get("UserName")
            first_name = record.get("FirstName")
            last_name = record.get("LastName")
            emails = ", ".join(record.get("Emails", []))
            
            print(f"  - Đang xử lý bản ghi SAP ID: {username}")
            
            # BIẾN DỮ LIỆU CÓ CẤU TRÚC THÀNH VĂN BẢN (Cho RAG hiểu được)
            text_chunk = f"Hồ sơ nhân sự SAP:\n- Tên tài khoản: {username}\n- Họ và tên: {first_name} {last_name}\n- Liên hệ: {emails}\n- Cập nhật lúc: {datetime.now().isoformat()}"
            extracted_texts.append(text_chunk)
            
            print("    -> Đã chuyển đổi thành đoạn văn (Text Chunk).")
            
        return extracted_texts
            
    except Exception as e:
        print(f"[!] Lỗi kết nối OData API: {e}")
        return []

def main():
    print("=== SAP ERP DATA CONNECTOR ===")
    chunks = fetch_sap_data()
    if chunks:
        print("\n[+] ĐÃ SẴN SÀNG ĐỂ NẠP VÀO CHROMADB:")
        print("--------------------------------------------------")
        print(chunks[0])
        print("--------------------------------------------------")

if __name__ == "__main__":
    main()
