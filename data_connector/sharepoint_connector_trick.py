import os
import sys
import msal
import requests
import json
import shutil

# --- CẤU HÌNH XÁC THỰC MICROSOFT GRAPH ---
CLIENT_ID = "f0644e97-688e-45e4-9b7a-0fe9b4399da8"
AUTHORITY = "https://login.microsoftonline.com/common"
SCOPES = ["Files.Read", "User.Read"]

TOKEN_CACHE_FILE = "sharepoint_token_cache.bin"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloaded_docs")
ARCHIVE_DIR = os.path.join(os.getcwd(), "archive")

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)

# --- XỬ LÝ AUTHENTICATION ---
def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        cache.deserialize(open(TOKEN_CACHE_FILE, "r").read())
    return cache

def save_cache(cache):
    if cache.has_state_changed:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(cache.serialize())

def authenticate():
    cache = load_cache()
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result:
            save_cache(cache)
            return result["access_token"]

    print("[*] Bắt đầu xác thực qua Device Flow...")
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        print("[!] Không thể tạo phiên đăng nhập.")
        return None

    print(f"\n[!!!] YÊU CẦU ĐĂNG NHẬP: {flow['message']}")
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        save_cache(cache)
        return result["access_token"]
    else:
        print(f"[!] Xác thực thất bại: {result.get('error_description', 'Unknown error')}")
        return None

# --- TÍNH NĂNG CONNECTOR TRICK ---
def list_and_download_files(token):
    print("\n[*] Đang quét thư mục 'RSVP' (OneDrive / SharePoint)...")
    url = "https://graph.microsoft.com/v1.0/me/drive/root:/RSVP:/children"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[!] Lỗi API: {response.status_code} - {response.text}")
        return

    files = response.json().get("value", [])
    print(f"[+] Tìm thấy {len(files)} mục trong thư mục.")

    document_files = [f for f in files if "file" in f]
    
    if not document_files:
        print("[*] Thư mục trống, không có tài liệu nào.")
        return

    print(f"[+] Phát hiện {len(document_files)} tài liệu. Đang tải về...\n")
    
    for file_item in document_files:
        file_name = file_item["name"]
        last_modified = file_item["lastModifiedDateTime"]
        download_url = file_item.get("@microsoft.graph.downloadUrl")

        print(f"  - Đang xử lý: {file_name}")
        print(f"    + Cập nhật lần cuối: {last_modified}")
        
        if download_url:
            # === BẮT ĐẦU ĐOẠN TRICK OFFLINE ===
            archive_file_path = os.path.join(ARCHIVE_DIR, file_name)
            save_path = os.path.join(DOWNLOAD_DIR, file_name)
            
            # Kiểm tra xem file có tồn tại trong thư mục archive do bạn upload trước không
            if os.path.exists(archive_file_path):
                print(f"    -> [Trick] Tìm thấy file '{file_name}' trong archive, đang copy giả lập tải về...")
                shutil.copy2(archive_file_path, save_path)
                print(f"    -> Đã lưu tại: {save_path}")
            else:
                print(f"    -> [Bỏ qua] Không tải file này (bỏ qua lệnh tải qua mạng để tránh lỗi SSL).")
            # === KẾT THÚC ĐOẠN TRICK OFFLINE ===
        else:
            print("    -> [!] File không hỗ trợ tải trực tiếp.")

def main():
    print("=== SHAREPOINT DATA CONNECTOR (TRICK OFFLINE DEMO) ===")
    token = authenticate()
    if not token:
        sys.exit(1)
        
    print("[+] Lấy Token thành công!")
    list_and_download_files(token)

if __name__ == "__main__":
    main()
