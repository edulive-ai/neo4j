import json

def generate_mock_users(count=1000):
    users = []
    for i in range(1, count + 1):
        user = {
            "name": f"Người dùng {i}",
            "email": f"user{i}@example.com",
            "age": 20 + (i % 50) # Tuổi từ 20 đến 69, thay đổi theo vòng lặp
        }
        users.append(user)
    
    # Dữ liệu payload hoàn chỉnh
    payload = {
        "users": users
        # Bạn có thể thêm "batch_size": giá_trị_mong_muốn ở đây nếu cần
        # ví dụ: "batch_size": 200
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)

# Tạo JSON cho 1000 người dùng
json_output_1000_users = generate_mock_users(30)
# print(json_output_1000_users)
with open("30_users.json", "w", encoding="utf-8") as f:
     f.write(json_output_1000_users)
