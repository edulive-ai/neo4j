# EducationSystem Class Documentation

## 📋 Overview

**EducationSystem** là một Python class hoàn chỉnh để quản lý hệ thống giáo dục trực tiếp với Neo4j database, không cần API.

### 🎯 Tính năng chính:
- **User Management**: Quản lý người dùng (CRUD, bulk operations với custom ID)
- **Test System**: Tạo và quản lý bài kiểm tra
- **Knowledge Management**: Quản lý kiến thức và tiến độ học tập
- **Analytics**: Thống kê và phân tích dữ liệu
- **Hierarchy Management**: Quản lý cấu trúc học liệu

---

## 🚀 Quick Start

### Installation & Setup

```python
# Cài đặt dependencies
pip install neo4j python-dotenv

# Import class
from education_system import EducationSystem

# Khởi tạo đơn giản (sử dụng config mặc định)
edu_system = EducationSystem()

# Hoặc với custom config
edu_system = EducationSystem(
    uri="neo4j://your-server:7687",
    username="your-username",
    password="your-password"
)

# Sử dụng với context manager (recommended)
with EducationSystem() as edu:
    # Your code here
    pass
```

### Environment Variables

Tạo file `.env`:
```bash
NEO4J_URI=neo4j://14.232.211.211:17687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=OPGk80GA26Q4
```

---

## 👥 User Management

### Create User

```python
with EducationSystem() as edu:
    # Tạo user mới (auto-generate ID)
    result = edu.create_user(
        name="Nguyễn Văn A",
        email="student_a@example.com", 
        age=8
    )
    
    # Tạo user với custom ID
    result = edu.create_user(
        name="Nguyễn Văn B",
        email="student_b@example.com", 
        age=9,
        user_id="STUDENT_001"
    )
    
    if result['success']:
        user = result['user']
        print(f"User created: {user['id']}")
    else:
        print(f"Error: {result['error']}")
```

**Parameters:**
- `name` (required): Tên học sinh
- `email` (required): Email (phải unique)
- `age` (optional): Tuổi (default: 7)
- `user_id` (optional): Custom ID (nếu không cung cấp sẽ auto-generate UUID)

**Returns:**
```python
{
    'message': 'User created successfully',
    'user': {
        'id': 'STUDENT_001',  # hoặc UUID nếu không cung cấp custom ID
        'name': 'Nguyễn Văn A',
        'email': 'student_a@example.com',
        'age': 8,
        'createdAt': '2024-01-01T10:00:00',
        'updatedAt': '2024-01-01T10:00:00'
    },
    'success': True
}
```

### Get Users

```python
with EducationSystem() as edu:
    # Lấy tất cả users
    users = edu.get_users()
    print(f"Total users: {users['count']}")
    
    # Lấy user theo ID
    user = edu.get_user_by_id("STUDENT_001")
    
    # Lấy user theo email
    user = edu.get_user_by_email("student@example.com")
```

### Bulk Create Users với Custom ID

```python
with EducationSystem() as edu:
    users_data = [
        {
            "id": "STUDENT_001",  # Custom ID
            "name": "Nguyễn Văn A", 
            "email": "student_a@example.com", 
            "age": 7
        },
        {
            "id": "STUDENT_002",  # Custom ID
            "name": "Trần Thị B", 
            "email": "student_b@example.com", 
            "age": 8
        },
        {
            # Không có ID -> sẽ auto-generate UUID
            "name": "Lê Văn C", 
            "email": "student_c@example.com", 
            "age": 9
        }
    ]
    
    result = edu.bulk_create_users(users_data, batch_size=1000)
    
    print(f"Created: {result['total_created']}")
    print(f"Errors: {result['total_errors']}")
    if result['errors']:
        for error in result['errors']:
            print(f"  - {error}")
```

**Tính năng nâng cao của bulk_create_users:**
- Hỗ trợ custom ID hoặc auto-generate UUID
- Validation ID và email trùng lặp trong batch
- Kiểm tra ID và email đã tồn tại trong database
- Xử lý lỗi chi tiết cho từng user
- Transaction safety với rollback

**Validation Rules:**
- `name` và `email` là bắt buộc
- Email phải chứa ký tự `@`
- Custom ID không được rỗng (nếu cung cấp)
- Không được trùng ID trong cùng batch
- Không được trùng ID hoặc email với database

---

## 🧪 Test System

### Create Complete Test

```python
with EducationSystem() as edu:
    # Định nghĩa câu hỏi
    questions = [
        {
            "question": "2 + 3 bằng bao nhiêu?",
            "answer": "5",
            "student_answer": "5",
            "is_correct": True,
            "points": 1,
            "difficulty": "easy",
            "duration_seconds": 30
        },
        {
            "question": "Đếm số lượng quả táo trong hình?",
            "answer": "4 quả táo",
            "image_question": "images/apples.jpg",
            "image_answer": "images/answer.jpg",
            "student_answer": "3 quả",
            "is_correct": False,
            "points": 2,
            "difficulty": "medium",
            "duration_seconds": 45
        },
        {
            "question": "Hình nào là hình vuông?",
            "answer": "Hình A",
            "image_question": "images/shapes.png",
            "student_answer": "Hình A",
            "is_correct": True,
            "points": 1,
            "difficulty": "easy",
            "duration_seconds": 25
        }
    ]
    
    # Tạo test hoàn chỉnh (có thể sử dụng custom user ID)
    result = edu.create_complete_test(
        title="Bài kiểm tra Toán lớp 1",
        description="Test các phép tính cơ bản và nhận biết hình học",
        user_id="STUDENT_001",  # Custom ID hoặc UUID
        questions=questions,
        duration_minutes=30
    )
    
    if result['success']:
        test_id = result['test']['id']
        summary = result['summary']
        print(f"Test created: {test_id}")
        print(f"Score: {summary['total_score']}")
        print(f"Accuracy: {summary['accuracy_percentage']}%")
```

**Required Question Fields:**
- `question`: Nội dung câu hỏi
- `answer`: Đáp án đúng
- `student_answer`: Câu trả lời của học sinh
- `is_correct`: True/False

**Optional Question Fields:**
- `image_question`: URL hình ảnh câu hỏi
- `image_answer`: URL hình ảnh đáp án
- `points`: Điểm số (default: 1)
- `difficulty`: "easy", "medium", "hard" (default: "medium")
- `duration_seconds`: Thời gian làm (default: 0)

### Get User Test History

```python
with EducationSystem() as edu:
    # Có thể sử dụng custom user ID
    history = edu.get_user_test_history("STUDENT_001")
    
    if history['success']:
        user = history['user']
        tests = history['test_history']
        
        print(f"Student: {user['name']}")
        print(f"Total tests: {history['total_tests']}")
        
        for test in tests:
            test_info = test['test']
            summary = test['summary']
            
            print(f"\nTest: {test_info['title']}")
            print(f"Date: {test_info['created_at']}")
            print(f"Questions: {summary['total_questions']}")
            print(f"Correct: {summary['correct_answers']}")
            print(f"Accuracy: {summary['accuracy_percentage']}%")
            
            # In chi tiết từng câu hỏi
            for qa in test['questions_and_answers']:
                question = qa['question']
                answer = qa['answer']
                status = "✅" if answer['is_correct'] else "❌"
                
                print(f"  {status} {question['content']}")
                print(f"     Student: {answer['student_answer']}")
                print(f"     Correct: {question['correct_answer']}")
```

### Get Test Details

```python
with EducationSystem() as edu:
    details = edu.get_test_details("test-uuid")
    
    if details['success']:
        test = details['test']
        user = details['user']
        summary = details['summary']
        difficulty_analysis = details['difficulty_analysis']
        
        print(f"Test: {test['title']}")
        print(f"Student: {user['name']}")
        print(f"Accuracy: {summary['accuracy_rate']}%")
        print(f"Time spent: {summary['total_time_spent']} seconds")
        
        # Phân tích theo độ khó
        print("\nPerformance by Difficulty:")
        for difficulty, stats in difficulty_analysis.items():
            print(f"  {difficulty}: {stats['correct']}/{stats['total']} ({stats['accuracy_rate']}%)")
```

### Search Tests

```python
with EducationSystem() as edu:
    # Tìm tất cả test của một user (có thể dùng custom ID)
    results = edu.search_tests(user_id="STUDENT_001")
    
    # Tìm test theo tiêu đề
    results = edu.search_tests(title_search="Toán")
    
    # Tìm test theo độ chính xác
    results = edu.search_tests(min_score=80, max_score=100)
    
    # Tìm test trong khoảng thời gian
    results = edu.search_tests(
        from_date="2024-01-01",
        to_date="2024-12-31"
    )
    
    # Kết hợp nhiều tiêu chí
    results = edu.search_tests(
        user_id="STUDENT_001",
        title_search="Toán",
        min_score=60
    )
    
    if results['success']:
        print(f"Found {results['count']} tests")
        for test in results['tests']:
            print(f"- {test['title']} ({test['accuracy_percentage']}%)")
```

---

## 📊 Analytics

### User Analytics

```python
with EducationSystem() as edu:
    # Có thể sử dụng custom user ID
    analytics = edu.get_user_analytics("STUDENT_001")
    
    if analytics['success']:
        user = analytics['user']
        stats = analytics['overall_statistics']
        difficulty_perf = analytics['difficulty_performance']
        
        print(f"Analytics for: {user['name']}")
        print(f"Total tests: {stats['total_tests']}")
        print(f"Questions answered: {stats['total_questions_answered']}")
        print(f"Overall accuracy: {stats['overall_accuracy']}%")
        print(f"Study time: {stats['total_study_time']} seconds")
        
        print("\nPerformance by Difficulty:")
        for perf in difficulty_perf:
            difficulty = perf['difficulty_level']
            accuracy = perf['accuracy_rate']
            total = perf['total_questions']
            print(f"  {difficulty}: {accuracy}% ({total} questions)")
```

### System Analytics

```python
with EducationSystem() as edu:
    analytics = edu.get_system_analytics()
    
    if analytics['success']:
        stats = analytics['overall_statistics']
        top_users = analytics['top_active_users']
        performance_dist = analytics['performance_distribution']
        
        print("System Overview:")
        print(f"  Total users: {stats['total_users']}")
        print(f"  Total tests: {stats['total_tests']}")
        print(f"  System accuracy: {stats['system_accuracy']}%")
        
        print("\nTop Active Users:")
        for user in top_users[:5]:
            print(f"  {user['user_name']}: {user['tests_taken']} tests")
        
        print("\nPerformance Distribution:")
        for range_name, count in performance_dist.items():
            print(f"  {range_name}: {count} tests")
```

---

## 🧠 Knowledge Management

### Create Knowledge

```python
with EducationSystem() as edu:
    result = edu.create_knowledge(
        name="Phép cộng cơ bản",
        subject="Toán",
        grade="Lớp 1",
        description="Kiến thức về phép cộng các số từ 1-10",
        order=1
    )
    
    if result['success']:
        knowledge = result['knowledge']
        print(f"Knowledge created: {knowledge['id']}")
```

### Get Knowledge

```python
with EducationSystem() as edu:
    # Lấy tất cả knowledge
    all_knowledge = edu.get_knowledge()
    
    # Lọc theo subject
    math_knowledge = edu.get_knowledge(subject="Toán")
    
    # Lọc theo grade
    grade1_knowledge = edu.get_knowledge(grade="Lớp 1")
    
    # Lọc theo cả subject và grade
    math_grade1 = edu.get_knowledge(subject="Toán", grade="Lớp 1")
    
    if math_grade1['success']:
        print(f"Found {math_grade1['count']} knowledge items")
        for item in math_grade1['knowledge']:
            print(f"- {item['name']} (Order: {item['order']})")
```

### Link User to Knowledge

```python
with EducationSystem() as edu:
    # Có thể sử dụng custom user ID
    result = edu.link_user_knowledge(
        user_id="STUDENT_001",
        knowledge_id="knowledge-uuid",
        status="learning",
        progress=25
    )
    
    if result['success']:
        link = result['link']
        print(f"Linked {link['user_name']} to {link['knowledge_name']}")
        print(f"Status: {link['relationship']['status']}")
        print(f"Progress: {link['relationship']['progress']}%")
```

### Get User Knowledge

```python
with EducationSystem() as edu:
    # Có thể sử dụng custom user ID
    user_knowledge = edu.get_user_knowledge("STUDENT_001")
    
    if user_knowledge['success']:
        user = user_knowledge['user']
        knowledge_list = user_knowledge['knowledge_list']
        
        print(f"Knowledge for {user['name']}:")
        print(f"Total: {user_knowledge['total_knowledge']} items")
        
        for item in knowledge_list:
            knowledge = item['knowledge']
            relationship = item['relationship']
            
            print(f"\n- {knowledge['name']}")
            print(f"  Subject: {knowledge['subject']}")
            print(f"  Grade: {knowledge['grade']}")
            print(f"  Status: {relationship['status']}")
            print(f"  Progress: {relationship['progress']}%")
            print(f"  Linked: {item['linked_date']}")
```

### Update Knowledge Progress

```python
with EducationSystem() as edu:
    # Cập nhật tiến độ (có thể sử dụng custom user ID)
    result = edu.update_user_knowledge_progress(
        user_id="STUDENT_001",
        knowledge_id="knowledge-uuid",
        progress=75,
        status="mastered"
    )
    
    if result['success']:
        update = result['update']
        print(f"Updated progress for {update['user_name']}")
        print(f"Knowledge: {update['knowledge_name']}")
        print(f"New progress: {update['relationship']['progress']}%")
        print(f"New status: {update['relationship']['status']}")
```

**Status values:**
- `"learning"`: Đang học
- `"completed"`: Hoàn thành  
- `"mastered"`: Thành thạo
- `"reviewing"`: Đang ôn tập

---

## 📚 Hierarchy Management

### Get Hierarchy Data

```python
with EducationSystem() as edu:
    # Lấy subjects
    subjects = edu.get_subjects()
    print(f"Subjects: {subjects['count']}")
    
    # Lấy typebooks (với hoặc không filter)
    all_typebooks = edu.get_typebooks()
    math_typebooks = edu.get_typebooks(subject_id="math-uuid")
    
    # Lấy chapters
    all_chapters = edu.get_chapters()
    book_chapters = edu.get_chapters(typebook_id="book-uuid")
    
    # Lấy lessons  
    all_lessons = edu.get_lessons()
    chapter_lessons = edu.get_lessons(chapter_id="chapter-uuid")
    
    # In cấu trúc hierarchy
    if subjects['success']:
        for subject in subjects['subjects']:
            print(f"Subject: {subject['name']}")
```

---

## 🔧 Utility Functions

### Export All Data

```python
with EducationSystem() as edu:
    export_data = edu.export_all_data()
    
    if export_data['success']:
        users = export_data['users']
        tests = export_data['tests']
        knowledge_links = export_data['knowledge_links']
        summary = export_data['summary']
        
        print(f"Exported at: {export_data['exported_at']}")
        print(f"Users: {summary['total_users']}")
        print(f"Tests: {summary['total_tests']}")
        print(f"Knowledge links: {summary['total_knowledge_links']}")
        
        # Lưu vào file
        import json
        with open('export_data.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
```

### Delete Test

```python
with EducationSystem() as edu:
    result = edu.delete_test("test-uuid")
    
    if result['success']:
        print(f"Deleted test: {result['test_id']}")
    else:
        print(f"Error: {result['error']}")
```

### Cleanup Orphaned Nodes

```python
with EducationSystem() as edu:
    cleanup = edu.cleanup_orphaned_nodes()
    
    if cleanup['success']:
        print(f"Cleanup completed:")
        print(f"  Deleted questions: {cleanup['deleted_questions']}")
        print(f"  Deleted answers: {cleanup['deleted_answers']}")
        print(f"  Total deleted: {cleanup['total_deleted']}")
```

### Health Check

```python
with EducationSystem() as edu:
    health = edu.health_check()
    
    if health['success']:
        print("✅ System is healthy")
    else:
        print(f"❌ System error: {health['error']}")
```

---

## 💡 Complete Example Workflow với Custom ID

```python
from education_system import EducationSystem

def main():
    """Complete workflow example với custom ID support"""
    
    with EducationSystem() as edu:
        # 1. Kiểm tra sức khỏe hệ thống
        health = edu.health_check()
        print(f"Health: {health['status']}")
        
        # 2. Tạo users với custom ID
        users_data = [
            {
                "id": "STUDENT_001",
                "name": "Nguyễn Văn A", 
                "email": "student_a@example.com", 
                "age": 7
            },
            {
                "id": "STUDENT_002", 
                "name": "Trần Thị B", 
                "email": "student_b@example.com", 
                "age": 8
            },
            {
                # Không có ID -> auto-generate
                "name": "Lê Văn C",
                "email": "student_c@example.com",
                "age": 9
            }
        ]
        
        users_result = edu.bulk_create_users(users_data)
        print(f"Created {users_result['total_created']} users")
        
        if users_result['errors']:
            print("Errors:")
            for error in users_result['errors']:
                print(f"  - {error}")
        
        # 3. Sử dụng custom user ID để tạo test
        if users_result['total_created'] > 0:
            user_id = "STUDENT_001"  # Sử dụng custom ID
            
            questions = [
                {
                    "question": "1 + 1 = ?",
                    "answer": "2",
                    "student_answer": "2",
                    "is_correct": True,
                    "points": 1,
                    "difficulty": "easy"
                },
                {
                    "question": "3 + 2 = ?", 
                    "answer": "5",
                    "student_answer": "4",
                    "is_correct": False,
                    "points": 1,
                    "difficulty": "easy"
                }
            ]
            
            test_result = edu.create_complete_test(
                title="Bài test mẫu",
                description="Test demo với custom user ID",
                user_id=user_id,
                questions=questions
            )
            
            if test_result['success']:
                print(f"Test created for user {user_id}: {test_result['test']['id']}")
                print(f"Score: {test_result['summary']['total_score']}")
                
                # 4. Xem lịch sử test với custom user ID
                history = edu.get_user_test_history(user_id)
                print(f"User {user_id} has {history['total_tests']} tests")
                
                # 5. Tạo knowledge và link với user (custom ID)
                knowledge_result = edu.create_knowledge(
                    name="Phép cộng cơ bản",
                    subject="Toán",
                    grade="Lớp 1"
                )
                
                if knowledge_result['success']:
                    knowledge_id = knowledge_result['knowledge']['id']
                    
                    link_result = edu.link_user_knowledge(
                        user_id=user_id,
                        knowledge_id=knowledge_id,
                        progress=50
                    )
                    
                    if link_result['success']:
                        print(f"User {user_id} linked to knowledge successfully")
                
                # 6. Lấy analytics cho custom user ID
                analytics = edu.get_user_analytics(user_id)
                if analytics['success']:
                    stats = analytics['overall_statistics']
                    print(f"User {user_id} accuracy: {stats.get('overall_accuracy', 0)}%")
                
                # 7. Export dữ liệu
                export = edu.export_all_data()
                print(f"Exported {export['summary']['total_users']} users")

if __name__ == "__main__":
    main()
```

---

## ⚠️ Error Handling

### Common Patterns

```python
with EducationSystem() as edu:
    # Pattern 1: Check success flag
    result = edu.create_user("Test", "test@example.com", user_id="CUSTOM_001")
    if result['success']:
        user = result['user']
        print(f"Created user with ID: {user['id']}")
    else:
        print(f"Error: {result['error']}")
    
    # Pattern 2: Try-catch for exceptions
    try:
        result = edu.create_complete_test(...)
        if result['success']:
            # Process result
            pass
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Pattern 3: Validate before processing
    users = edu.get_users()
    if users['success'] and users['count'] > 0:
        for user in users['users']:
            # Process each user
            pass
```

### Common Errors với Custom ID

- **"User ID already exists"**: Custom ID đã được sử dụng
- **"Duplicate ID in batch"**: Trùng ID trong cùng batch import
- **"Empty ID provided"**: Custom ID rỗng
- **"User not found"**: User ID không tồn tại (custom hoặc UUID)
- **"Email already exists"**: Email đã được sử dụng
- **"Test not found"**: Test ID không tồn tại
- **"Questions array cannot be empty"**: Thiếu questions
- **"Transaction failed"**: Lỗi database transaction

---

## 🚀 Best Practices

### 1. Always Use Context Manager

```python
# ✅ Good
with EducationSystem() as edu:
    # Your code here
    pass

# ❌ Avoid
edu = EducationSystem()
# ... code ...
# Forget to call edu.close()
```

### 2. Check Success Before Processing

```python
# ✅ Good
result = edu.create_user("Name", "email@example.com", user_id="STUDENT_001")
if result['success']:
    user_id = result['user']['id']
    # Continue processing
else:
    handle_error(result['error'])

# ❌ Avoid
result = edu.create_user("Name", "email@example.com") 
user_id = result['user']['id']  # May crash if not successful
```

### 3. Use Bulk Operations When Possible

```python
# ✅ Good - Bulk create với custom ID
users_data = [
    {"id": f"STUDENT_{i:03d}", "name": f"Student {i}", "email": f"student{i}@example.com"} 
    for i in range(1, 101)
]
result = edu.bulk_create_users(users_data)

# ❌ Avoid - Individual creates
for i in range(1, 101):
    edu.create_user(f"Student {i}", f"student{i}@example.com", user_id=f"STUDENT_{i:03d}")
```

### 4. Consistent ID Naming Convention

```python
# ✅ Good - Consistent naming
user_ids = [
    "STUDENT_001", "STUDENT_002", "STUDENT_003",
    "TEACHER_001", "ADMIN_001"
]

# ❌ Avoid - Inconsistent naming
user_ids = [
    "student1", "STUDENT_02", "Student_3", "teacher01"
]
```

### 5. Handle Custom ID Validation

```python
def validate_custom_id(custom_id, prefix="STUDENT"):
    """Validate custom ID format"""
    if not custom_id:
        return False, "ID cannot be empty"
    
    if not custom_id.startswith(prefix):
        return False, f"ID must start with {prefix}"
    
    if len(custom_id) != len(f"{prefix}_000"):
        return False, f"ID must follow format {prefix}_XXX"
    
    return True, None

# Use validation
custom_id = "STUDENT_001"
valid, error = validate_custom_id(custom_id)
if not valid:
    print(f"Invalid ID: {error}")
```

### 6. Mix Custom ID và Auto-Generate

```python
# ✅ Good - Flexible approach
users_data = [
    {"id": "TEACHER_001", "name": "Teacher A", "email": "teacher@school.com"},  # Custom
    {"name": "Student B", "email": "student@school.com"},  # Auto-generate
    {"id": "ADMIN_001", "name": "Admin C", "email": "admin@school.com"}  # Custom
]

result = edu.bulk_create_users(users_data)
```

---

## 📈 Performance Tips

### 1. Use Batch Operations với Custom ID
- Sử dụng `bulk_create_users()` với danh sách custom ID
- Set `batch_size` phù hợp (1000-5000 cho users)
- Validate ID trước khi gọi bulk operation

### 2. ID Indexing
- Custom ID nên ngắn gọn và có pattern
- Tránh sử dụng special characters trong custom ID
- Consider database indexing cho custom ID

### 3. Memory Management
- Với dataset lớn, chia nhỏ batch để tránh memory issues
- Clear unused variables sau bulk operations

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
NEO4J_URI=neo4j://your-server:7687
NEO4J_USERNAME=your-username
NEO4J_PASSWORD=your-password

# Optional
DEBUG=True
LOG_LEVEL=INFO
```

### Custom Configuration

```python
# Custom config
edu = EducationSystem(
    uri="neo4j://custom-server:7687",
    username="custom-user", 
    password="custom-password"
)

# Using environment variables
import os
edu = EducationSystem(
    uri=os.getenv("CUSTOM_NEO4J_URI"),
    username=os.getenv("CUSTOM_USERNAME"),
    password=os.getenv("CUSTOM_PASSWORD")
)
```

---

## 📝 Notes

- **Custom ID Support**: Class hỗ trợ đầy đủ custom ID cho users
- **Thread Safety**: Class không thread-safe, sử dụng instance riêng cho mỗi thread
- **Memory Usage**: Bulk operations với custom ID có thể sử dụng nhiều memory
- **ID Validation**: Luôn validate custom ID trước khi sử dụng
- **Backup**: Thường xuyên backup database và sử dụng `export_all_data()`
- **Custom ID Best Practices**: Sử dụng naming convention nhất quán
- **Network**: Đảm bảo kết nối ổn định đến Neo4j server

---

## 🆔 Custom ID Guidelines

### Recommended ID Patterns

```python
# Students
"STUDENT_001", "STUDENT_002", "STUDENT_999"

# Teachers  
"TEACHER_001", "TEACHER_002"

# Admins
"ADMIN_001", "ADMIN_002"

# Classes
"CLASS_1A", "CLASS_2B", "CLASS_3C"

# Schools
"SCHOOL_001", "SCHOOL_002"
```

### ID Generation Helper

```python
def generate_student_id(sequence_number):
    """Generate student ID with consistent format"""
    return f"STUDENT_{sequence_number:03d}"

def generate_teacher_id(sequence_number):
    """Generate teacher ID with consistent format"""
    return f"TEACHER_{sequence_number:03d}"

# Usage
student_ids = [generate_student_id(i) for i in range(1, 101)]
teacher_ids = [generate_teacher_id(i) for i in range(1, 11)]
```

### Bulk Import với Sequential ID

```python
def create_sequential_users(edu, prefix, start_num, count, base_name, base_email, age=7):
    """Create users with sequential custom IDs"""
    users_data = []
    
    for i in range(count):
        seq_num = start_num + i
        user_data = {
            "id": f"{prefix}_{seq_num:03d}",
            "name": f"{base_name} {seq_num}",
            "email": f"{base_email.split('@')[0]}{seq_num}@{base_email.split('@')[1]}",
            "age": age
        }
        users_data.append(user_data)
    
    return edu.bulk_create_users(users_data)

# Usage
with EducationSystem() as edu:
    # Tạo 50 học sinh với ID từ STUDENT_001 đến STUDENT_050
    result = create_sequential_users(
        edu=edu,
        prefix="STUDENT", 
        start_num=1, 
        count=50,
        base_name="Học sinh",
        base_email="student@school.com",
        age=8
    )
    
    print(f"Created {result['total_created']} students")
```

---

## 🔄 Migration & Import Strategies

### Import từ CSV với Custom ID

```python
import csv
from education_system import EducationSystem

def import_users_from_csv(csv_file_path):
    """Import users from CSV file with custom ID support"""
    users_data = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            user_data = {
                "id": row.get('id'),  # Custom ID from CSV
                "name": row['name'],
                "email": row['email'],
                "age": int(row.get('age', 7))
            }
            users_data.append(user_data)
    
    with EducationSystem() as edu:
        result = edu.bulk_create_users(users_data)
        return result

# CSV format:
# id,name,email,age
# STUDENT_001,Nguyễn Văn A,student1@school.com,8
# STUDENT_002,Trần Thị B,student2@school.com,7
# ,Lê Văn C,student3@school.com,9  # Empty ID -> auto-generate
```

### Migrate từ System Cũ

```python
def migrate_from_old_system(old_system_data):
    """Migrate users from old system with ID mapping"""
    users_data = []
    id_mapping = {}  # Track old_id -> new_id mapping
    
    for old_user in old_system_data:
        # Generate new custom ID based on old system
        old_id = old_user['old_id']
        new_id = f"MIGRATED_{old_id}"
        
        user_data = {
            "id": new_id,
            "name": old_user['full_name'],
            "email": old_user['email_address'],
            "age": old_user.get('age', 7)
        }
        
        users_data.append(user_data)
        id_mapping[old_id] = new_id
    
    with EducationSystem() as edu:
        result = edu.bulk_create_users(users_data)
        
        if result['success']:
            print(f"Migrated {result['total_created']} users")
            return id_mapping
        else:
            print(f"Migration failed: {result['error']}")
            return None
```

---

## 🧪 Testing với Custom ID

### Unit Test Examples

```python
import unittest
from education_system import EducationSystem

class TestEducationSystemCustomID(unittest.TestCase):
    
    def setUp(self):
        self.edu = EducationSystem()
    
    def tearDown(self):
        self.edu.close()
    
    def test_create_user_with_custom_id(self):
        """Test creating user with custom ID"""
        result = self.edu.create_user(
            name="Test User",
            email="test@example.com",
            user_id="TEST_001"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user']['id'], "TEST_001")
    
    def test_bulk_create_mixed_ids(self):
        """Test bulk create with mix of custom and auto-generated IDs"""
        users_data = [
            {"id": "BULK_001", "name": "User 1", "email": "user1@test.com"},
            {"name": "User 2", "email": "user2@test.com"},  # No ID
            {"id": "BULK_003", "name": "User 3", "email": "user3@test.com"}
        ]
        
        result = self.edu.bulk_create_users(users_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_created'], 3)
        self.assertEqual(result['total_errors'], 0)
    
    def test_duplicate_custom_id_error(self):
        """Test error handling for duplicate custom ID"""
        # Create first user
        self.edu.create_user("User 1", "user1@test.com", user_id="DUP_001")
        
        # Try to create second user with same ID
        result = self.edu.create_user("User 2", "user2@test.com", user_id="DUP_001")
        
        self.assertFalse(result['success'])
        self.assertIn("already exists", result['error'])

if __name__ == '__main__':
    unittest.main()
```

### Load Testing với Custom ID

```python
import time
from concurrent.futures import ThreadPoolExecutor
from education_system import EducationSystem

def load_test_bulk_create(batch_size=1000, total_users=10000):
    """Load test bulk create with custom IDs"""
    
    def create_batch(batch_start, batch_size):
        users_data = []
        for i in range(batch_size):
            user_num = batch_start + i
            users_data.append({
                "id": f"LOAD_TEST_{user_num:06d}",
                "name": f"Load Test User {user_num}",
                "email": f"loadtest{user_num}@example.com",
                "age": 8
            })
        
        with EducationSystem() as edu:
            start_time = time.time()
            result = edu.bulk_create_users(users_data)
            end_time = time.time()
            
            return {
                'batch_start': batch_start,
                'duration': end_time - start_time,
                'created': result['total_created'],
                'errors': result['total_errors']
            }
    
    # Execute batches
    batches = []
    for i in range(0, total_users, batch_size):
        batches.append((i, min(batch_size, total_users - i)))
    
    total_start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda b: create_batch(b[0], b[1]), batches))
    
    total_end_time = time.time()
    
    # Calculate statistics
    total_created = sum(r['created'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    total_duration = total_end_time - total_start_time
    avg_batch_duration = sum(r['duration'] for r in results) / len(results)
    
    print(f"Load Test Results:")
    print(f"  Total users: {total_users}")
    print(f"  Total created: {total_created}")
    print(f"  Total errors: {total_errors}")
    print(f"  Total duration: {total_duration:.2f}s")
    print(f"  Average batch duration: {avg_batch_duration:.2f}s")
    print(f"  Users per second: {total_created / total_duration:.2f}")

# Run load test
if __name__ == "__main__":
    load_test_bulk_create(batch_size=1000, total_users=10000)
```

---

## 🔍 Monitoring & Debugging

### Debug Custom ID Issues

```python
def debug_user_creation_issues(users_data):
    """Debug common issues with custom ID user creation"""
    
    issues = []
    seen_ids = set()
    seen_emails = set()
    
    for i, user in enumerate(users_data):
        user_issues = []
        
        # Check required fields
        if 'name' not in user or not user['name'].strip():
            user_issues.append("Missing or empty name")
        
        if 'email' not in user or '@' not in user['email']:
            user_issues.append("Invalid email format")
        
        # Check custom ID
        if 'id' in user:
            user_id = user['id']
            if not user_id or not str(user_id).strip():
                user_issues.append("Empty custom ID")
            elif user_id in seen_ids:
                user_issues.append(f"Duplicate ID: {user_id}")
            else:
                seen_ids.add(user_id)
        
        # Check email duplicates
        email = user.get('email', '').lower()
        if email in seen_emails:
            user_issues.append(f"Duplicate email: {email}")
        else:
            seen_emails.add(email)
        
        if user_issues:
            issues.append({
                'user_index': i,
                'user_data': user,
                'issues': user_issues
            })
    
    return issues

# Usage
users_data = [
    {"id": "TEST_001", "name": "User 1", "email": "user1@test.com"},
    {"id": "TEST_001", "name": "User 2", "email": "user2@test.com"},  # Duplicate ID
    {"id": "", "name": "User 3", "email": "user3@test.com"},  # Empty ID
    {"name": "User 4", "email": "invalid-email"}  # Invalid email
]

issues = debug_user_creation_issues(users_data)
for issue in issues:
    print(f"User {issue['user_index']}: {', '.join(issue['issues'])}")
```

### Monitor System Performance

```python
def monitor_system_performance(edu):
    """Monitor system performance and custom ID usage"""
    
    # Get system analytics
    analytics = edu.get_system_analytics()
    
    if analytics['success']:
        stats = analytics['overall_statistics']
        
        print("📊 System Performance Report:")
        print(f"  Total Users: {stats.get('total_users', 0)}")
        print(f"  Total Tests: {stats.get('total_tests', 0)}")
        print(f"  System Accuracy: {stats.get('system_accuracy', 0)}%")
    
    # Check for custom ID patterns
    with edu.driver.session() as session:
        # Analyze ID patterns
        id_patterns = session.run("""
            MATCH (u:User)
            WITH u.id as user_id
            WITH CASE 
                WHEN user_id STARTS WITH 'STUDENT_' THEN 'STUDENT'
                WHEN user_id STARTS WITH 'TEACHER_' THEN 'TEACHER'
                WHEN user_id STARTS WITH 'ADMIN_' THEN 'ADMIN'
                WHEN length(user_id) = 36 AND user_id CONTAINS '-' THEN 'UUID'
                ELSE 'OTHER'
            END as id_type
            RETURN id_type, count(*) as count
            ORDER BY count DESC
        """)
        
        print("\n🆔 ID Pattern Analysis:")
        for record in id_patterns:
            print(f"  {record['id_type']}: {record['count']} users")
        
        # Check for potential ID conflicts
        duplicate_check = session.run("""
            MATCH (u:User)
            WITH u.id as user_id, count(*) as count
            WHERE count > 1
            RETURN user_id, count
        """)
        
        duplicates = list(duplicate_check)
        if duplicates:
            print("\n⚠️  Duplicate IDs Found:")
            for record in duplicates:
                print(f"  ID '{record['user_id']}': {record['count']} instances")
        else:
            print("\n✅ No duplicate IDs found")

# Usage
with EducationSystem() as edu:
    monitor_system_performance(edu)
```

---

## 📋 Checklist for Production

### Pre-deployment Checklist

- [ ] **Environment Variables**: Đã cấu hình đúng NEO4J_URI, username, password
- [ ] **Custom ID Convention**: Đã định nghĩa và document ID naming convention
- [ ] **Validation Rules**: Đã implement validation cho custom ID format
- [ ] **Error Handling**: Đã test error scenarios (duplicate ID, invalid format)
- [ ] **Performance Testing**: Đã test bulk operations với dataset lớn
- [ ] **Backup Strategy**: Đã có plan backup và recovery
- [ ] **Monitoring**: Đã setup monitoring cho ID conflicts và performance
- [ ] **Documentation**: Đã update documentation với custom ID examples

### Security Checklist

- [ ] **ID Predictability**: Custom ID không dễ đoán (nếu cần security)
- [ ] **Input Validation**: Validate và sanitize custom ID input
- [ ] **Access Control**: Kiểm soát quyền truy cập theo user role
- [ ] **Audit Trail**: Log các operations với custom ID
- [ ] **Data Privacy**: Đảm bảo custom ID không chứa thông tin nhạy cảm

---

*Last Updated: May 28, 2025*
*Version: 2.0 - Added Custom ID Support*