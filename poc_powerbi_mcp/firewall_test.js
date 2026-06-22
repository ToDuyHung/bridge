const https = require('https');

const endpoints = [
    { name: "Microsoft Login (Azure AD)", url: "https://login.microsoftonline.com" },
    { name: "PowerBI API", url: "https://api.powerbi.com" }
];

console.log("=========================================");
console.log("Bắt đầu kiểm tra kết nối mạng (Firewall Test)");
console.log("=========================================\n");

endpoints.forEach(endpoint => {
    console.log(`Đang kiểm tra kết nối tới: ${endpoint.name} (${endpoint.url})`);
    const req = https.get(endpoint.url, (res) => {
        if (res.statusCode === 200 || res.statusCode === 302 || res.statusCode === 404) {
            // 404 is still a valid response from the server meaning network is open
            console.log(`[PASS] Kết nối thành công tới ${endpoint.name}! (HTTP Status: ${res.statusCode})\n`);
        } else {
            console.log(`[WARNING] Đã kết nối được tới ${endpoint.name} nhưng nhận mã lỗi: ${res.statusCode}\n`);
        }
    });

    req.on('error', (e) => {
        console.error(`[FAIL] LỖI KẾT NỐI TỚI ${endpoint.name}:`);
        console.error(`Chi tiết lỗi: ${e.message}`);
        console.error(`-> Hành động: Vui lòng nhờ đội ngũ IT / NetOps mở Firewall Outbound cho domain này.\n`);
    });
    
    req.setTimeout(5000, () => {
        console.error(`[FAIL] KẾT NỐI TIMEOUT TỚI ${endpoint.name}:`);
        console.error(`-> Hành động: Tường lửa (Firewall) đang chặn hoặc mạng quá chậm.\n`);
        req.destroy();
    });
});
