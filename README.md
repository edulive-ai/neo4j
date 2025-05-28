# Neo4j Education System - Hướng dẫn sử dụng

Bộ công cụ quản lý và thao tác dữ liệu giáo dục với Neo4j cho ứng dụng học tập.

---

## 1. Cài đặt

1. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

2. Tạo file `.env` với thông tin kết nối:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

---

## 2. Quy trình chuẩn sử dụng hệ thống

### Bước 1: Import dữ liệu mẫu

**File:** `add_data.py`

- Chức năng: Import dữ liệu mẫu (users, grade, subject, typebook, chapter, lesson, question, answer) vào Neo4j.
- Sử dụng:
  ```bash
  python add_data.py
  ```
- Kết quả: Database có đầy đủ cấu trúc dữ liệu nền tảng.

---

### Bước 2: Tạo các node kiến thức (Knowledge)

**File:** `create_knowledge.py`

- Chức năng: Tạo các node kiến thức (Knowledge) cho môn Toán lớp 1 vào Neo4j.
- Sử dụng:
  ```bash
  python create_knowledge.py
  ```
- Kết quả: Database có thêm các node kiến thức phục vụ phân tích, gán kiến thức cho học sinh.

---

### Bước 3: Sử dụng API thao tác với Neo4j

**File:** `api_neo4j.py`

- Chức năng: Cung cấp các endpoint API RESTful để thao tác với database Neo4j (CRUD users, questions, answers, tests, knowledge, analytics...)
- Sử dụng:
  ```bash
  python api_neo4j.py
  ```
- Kết quả: Server API Flask chạy tại `http://localhost:5000` để frontend hoặc hệ thống khác có thể gọi tới.

---

### Bước 4: Sử dụng module Python thao tác trực tiếp với Neo4j

**File:** `neo4j_module.py`

- Chức năng: Cung cấp class `EducationSystem` để thao tác trực tiếp với database Neo4j trong các script Python nội bộ (không cần API).
- Sử dụng ví dụ:
  ```python
  from neo4j_module import EducationSystem

  edu = EducationSystem()
  # Tạo user
  result = edu.create_user(name="Nguyễn Văn A", email="a@example.com")
  # Tạo test, truy vấn, phân tích...
  edu.close()
  ```
- Kết quả: Dùng cho các script tự động, phân tích, import/export, hoặc các tác vụ nội bộ.

---

## 3. Lưu ý quan trọng

- **Không nên chạy lại `add_data.py` hoặc `create_knowledge.py` nhiều lần trên cùng một database nếu không muốn dữ liệu bị trùng lặp.**
- **Kiểm tra biến môi trường `.env` trước khi chạy các script.**
- **Có thể mở rộng thêm các chức năng cho từng file/module tùy nhu cầu thực tế.**

---

## 4. Ví dụ sử dụng nhanh với module

```python
from neo4j_module import EducationSystem

edu = EducationSystem()
user = edu.create_user(name="Nguyễn Văn B", email="b@example.com")
test = edu.create_complete_test(
    title="Test Toán",
    description="Kiểm tra cộng trừ",
    user_id=user['user']['id'],
    questions=[
        {"question": "2+2=?", "answer": "4", "student_answer": "4", "is_correct": True}
    ]
)
edu.close()
```

---

Nếu cần thêm ví dụ chi tiết hoặc hướng dẫn mở rộng, hãy liên hệ đội phát triển!
