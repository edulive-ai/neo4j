# Neo4j Database Tools

Bộ công cụ làm việc với cơ sở dữ liệu Neo4j cho ứng dụng học tập.

## Cài đặt

1. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

2. Tạo file `.env` với các thông tin kết nối:

```
NEO4J_URI=neo4j+s://your-database-id.databases.neo4j.io
NEO4J_USERNAME=your_username
NEO4J_PASSWORD=your_password
```

## Các công cụ

### 1. Tạo dữ liệu mẫu

Chạy lệnh sau để tạo dữ liệu mẫu trong cơ sở dữ liệu Neo4j:

```bash
python test_db_neo4j.py
```

### 2. Truy vấn dữ liệu

Để xem danh sách các truy vấn có sẵn:

```bash
python query_neo4j_data.py
```

Để chạy một truy vấn cụ thể:

```bash
python query_neo4j_data.py all_students
```

Để chạy tất cả các truy vấn:

```bash
python query_neo4j_data.py all
```

## Các truy vấn có sẵn

- `all_subjects`: Tất cả các môn học
- `all_students`: Tất cả học sinh
- `student_enrollments`: Thông tin đăng ký môn học
- `all_questions`: Tất cả câu hỏi
- `question_answers`: Câu hỏi và đáp án
- `student_attempts`: Bài làm của học sinh
- `student_performance`: Thống kê kết quả học tập
