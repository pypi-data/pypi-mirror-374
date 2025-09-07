# kmbbank

**Unofficial MB Bank API client for Python**  
Repackaged and maintained as **kmbbank**.

---

## 📌 Giới thiệu

`kmbbank` là một thư viện Python không chính thức giúp bạn tương tác với hệ thống ngân hàng **MB Bank** (Ngân hàng TMCP Quân đội) thông qua API.  

Thư viện này được fork lại từ [thedtvn/MBBank](https://github.com/thedtvn/MBBank), tinh chỉnh để dễ cài đặt, dễ dùng hơn và phân phối qua PyPI với tên gói ngắn gọn `kmbbank`.  

⚠️ **Lưu ý**: Đây là dự án cộng đồng, **không phải API chính thức của MB Bank**. Việc sử dụng có thể tiềm ẩn rủi ro (bị chặn truy cập, khóa tài khoản…). Vui lòng cân nhắc và tự chịu trách nhiệm khi dùng.

---

## ✨ Tính năng chính

- Đăng nhập tài khoản cá nhân MB Bank (qua API không chính thức).  
- Lấy danh sách tài khoản, số dư, lịch sử giao dịch.  
- Hỗ trợ OCR CAPTCHA qua gói [mb-capcha-ocr](https://pypi.org/project/mb-capcha-ocr/).  
- Dùng session/cookie để tái sử dụng phiên đăng nhập.  
- Viết bằng Python thuần, dễ mở rộng và tích hợp.

---

## ⚙️ Yêu cầu

- Python **3.8+**  
- Các thư viện phụ trợ: `requests`, `aiohttp`, `Pillow`, `wasmtime`, `mb-capcha-ocr`  
- Tuỳ chọn: [onnxruntime](https://onnxruntime.ai/getting-started) nếu bạn muốn dùng OCR tăng tốc với GPU (CUDA).

---

## 🚀 Cài đặt

Cài trực tiếp từ PyPI:

```bash
pip install kmbbank
