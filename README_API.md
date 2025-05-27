# Education API - Usage Guide

## 📋 Overview

**Neo4j Educational API** for managing educational content and student learning progress.

- **Base URL**: `http://localhost:5000`
- **Database**: Remote Neo4j at `neo4j://14.232.211.211:17687`
- **Authentication**: None required

## 🏗️ Data Model

```
Subject → TypeBook → Chapter → Lesson → Question
User → Answer → Question
User → Knowledge (learning progress)
```

---

## 🔌 How to Use the API

### 🏥 Health Check

```bash
GET /api/v1/health
```
Check if API and database are working.

---

## 👥 User Management

### Get All Users
```bash
GET /api/v1/users
```

### Create Single User
```bash
POST /api/v1/users
Content-Type: application/json

{
  "name": "Nguyễn Văn A",
  "email": "student@example.com",
  "age": 7
}
```

**Required fields**: `name`, `email`  
**Optional fields**: `age` (default: 7)

### Bulk Import Users
```bash
POST /api/v1/users/bulk
Content-Type: application/json

{
  "users": [
    {
      "name": "Student 1",
      "email": "student1@example.com",
      "age": 7
    },
    {
      "name": "Student 2", 
      "email": "student2@example.com",
      "age": 8
    }
  ],
  "batch_size": 1000
}
```

**Required in each user**: `name`, `email`  
**Optional**: `age`, `batch_size` (default: 1000)

---

## 📚 Hierarchy Management

### Get Subjects
```bash
GET /api/v1/subjects
```

### Get TypeBooks
```bash
# All typebooks
GET /api/v1/typebooks

# Filter by subject
GET /api/v1/typebooks?subject_id=your-subject-uuid
```

### Get Chapters
```bash
# All chapters
GET /api/v1/chapters

# Filter by typebook
GET /api/v1/chapters?typebook_id=your-typebook-uuid
```

### Get Lessons
```bash
# All lessons
GET /api/v1/lessons

# Filter by chapter
GET /api/v1/lessons?chapter_id=your-chapter-uuid
```

---

## ❓ Question Management

### Get Questions
```bash
# All questions
GET /api/v1/questions

# Filter by lesson
GET /api/v1/questions?lesson_id=your-lesson-uuid

# Filter by chapter
GET /api/v1/questions?chapter_id=your-chapter-uuid
```

### Bulk Import Questions
```bash
POST /api/v1/questions/bulk
Content-Type: application/json

{
  "questions": [
    {
      "lesson_id": "existing-lesson-uuid",
      "title": "Bài 1 trang 7 sách giáo khoa toán lớp 1",
      "content": "Dùng các từ: trên, dưới, trái, phải để nói về bức tranh?",
      "correct_answer": "Bạn Lan đang ngồi ở giữa bàn học...",
      "difficulty": "dễ",
      "page": 7,
      "image_question": "images/bai1-trang7-sgk.png",
      "image_answer": ""
    }
  ],
  "batch_size": 500
}
```

**Required fields**: `lesson_id`, `title`, `content`, `correct_answer`, `difficulty`, `page`  
**Optional fields**: `image_question`, `image_answer`, `batch_size`  
**Difficulty values**: `"dễ"`, `"trung bình"`, `"khó"`

---

## ✅ Answer Management

### Submit Answers (Bulk)
```bash
POST /api/v1/answers/bulk
Content-Type: application/json

{
  "answers": [
    {
      "user_id": "student-uuid",
      "question_id": "question-uuid",
      "student_answer": "Em thấy có 4 quả táo",
      "is_correct": true,
      "start_time": "2025-05-27T10:00:00.000000",
      "completion_time": "2025-05-27T10:02:00.000000",
      "duration_seconds": 120
    }
  ],
  "batch_size": 500
}
```

**Required fields**: `user_id`, `question_id`, `student_answer`, `is_correct`  
**Optional fields**: `start_time`, `completion_time`, `duration_seconds`, `batch_size`

---

## 🧠 Knowledge Management

### Get Knowledge
```bash
# All knowledge
GET /api/v1/knowledge

# Filter by subject and grade
GET /api/v1/knowledge?subject=Toán&grade=Lớp 1
```

### Create Knowledge
```bash
POST /api/v1/knowledge
Content-Type: application/json

{
  "name": "Trên - Dưới, Phải - Trái, Trước - Sau, Ở giữa",
  "description": "Kiến thức về vị trí không gian cơ bản",
  "order": 1,
  "subject": "Toán",
  "grade": "Lớp 1"
}
```

**Required fields**: `name`, `subject`, `grade`  
**Optional fields**: `description`, `order`

---

## 🔗 User-Knowledge Relationships

### Link User to Knowledge
```bash
POST /api/v1/users/{user_id}/knowledge/{knowledge_id}
```
Creates learning relationship with timestamp.

### Get User's Knowledge
```bash
GET /api/v1/users/{user_id}/knowledge
```

### Get Knowledge's Users
```bash
GET /api/v1/knowledge/{knowledge_id}/users
```

### Update Learning Progress
```bash
PUT /api/v1/users/{user_id}/knowledge/{knowledge_id}
Content-Type: application/json

{
  "progress": 75,
  "status": "learning"
}
```

**Optional fields**: `progress` (0-100), `status`  
**Status values**: `"learning"`, `"completed"`, `"mastered"`, `"reviewing"`

### Remove Link
```bash
DELETE /api/v1/users/{user_id}/knowledge/{knowledge_id}
```

### Bulk Link Users to Knowledge
```bash
POST /api/v1/users/bulk/knowledge
Content-Type: application/json

{
  "links": [
    {
      "user_id": "user1-uuid",
      "knowledge_id": "knowledge1-uuid",
      "status": "learning",
      "progress": 0
    },
    {
      "user_id": "user1-uuid",
      "knowledge_id": "knowledge2-uuid",
      "status": "learning", 
      "progress": 25
    }
  ]
}
```

**Required fields**: `user_id`, `knowledge_id`  
**Optional fields**: `status`, `progress`


## 🎓 Student Analytics

### Single Student Details
```bash
GET /api/v1/students/{user_id}/detailed
```

### Multiple Students Details
```bash
GET /api/v1/students/detailed?user_ids=id1,id2,id3&subject_id=math-uuid&limit=20
```

**Parameters**:
- `user_ids`: Comma-separated user IDs
- `subject_id`: Filter by subject
- `chapter_id`: Filter by chapter
- `lesson_id`: Filter by lesson
- `limit`: Max students (default: 20)

### Answer History
```bash
GET /api/v1/students/answers-history?user_id=student-uuid&from_date=2025-05-01&to_date=2025-05-31&difficulty=dễ&is_correct=false&limit=50
```

**Parameters**:
- `user_id`: Specific user
- `from_date`: Start date (YYYY-MM-DD)
- `to_date`: End date (YYYY-MM-DD)
- `difficulty`: Question difficulty
- `is_correct`: Filter by correctness (`true`/`false`)
- `limit`: Max records (default: 100)

### Learning Path
```bash
GET /api/v1/students/learning-path/{user_id}
```

---

## 📊 Analytics

### Hierarchy Analytics
```bash
GET /api/v1/analytics/hierarchy
```

### User Analytics
```bash
GET /api/v1/analytics/user/{user_id}
```

### System Summary
```bash
GET /api/v1/analytics/summary
```

### Subject Analytics
```bash
GET /api/v1/analytics/subject/{subject_id}
```

### User-Knowledge Analytics
```bash
GET /api/v1/users-knowledge/analytics
```

---

## 🌳 Tree Structure

### Complete Tree
```bash
GET /api/v1/tree?include_users=true&include_questions=true
```

**Parameters**:
- `include_users`: Include users list (default: true)
- `include_questions`: Include questions (default: true)

### IDs Only
```bash
GET /api/v1/tree/ids-only
```

### Flat Structure
```bash
GET /api/v1/tree/flat
```

---

## 📤 Export

### Export All Data
```bash
GET /api/v1/export
```

---

## 🔧 Configuration

### Environment Variables
```bash
NEO4J_URI=neo4j://14.232.211.211:17687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=OPGk80GA26Q4
PORT=5000
DEBUG=True
```

### Test Connection
```python
import os
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://14.232.211.211:17687",
    auth=("neo4j", "OPGk80GA26Q4")
)

with driver.session() as session:
    result = session.run("RETURN 'Connected!' as message")
    print(result.single()["message"])

driver.close()
```

---

## 🚀 Quick Start Examples

### 1. Complete Learning Workflow
```bash
# 1. Get subjects
GET /api/v1/subjects

# 2. Get questions for lesson
GET /api/v1/questions?lesson_id=lesson-uuid

# 3. Submit answers
POST /api/v1/answers/bulk
{
  "answers": [{
    "user_id": "student-uuid",
    "question_id": "question-uuid",
    "student_answer": "Answer text",
    "is_correct": true,
    "duration_seconds": 120
  }]
}

# 4. Check progress
GET /api/v1/students/student-uuid/detailed
```

### 2. Knowledge Management
```bash
# 1. Get knowledge
GET /api/v1/knowledge?subject=Toán&grade=Lớp 1

# 2. Link to student
POST /api/v1/users/student-uuid/knowledge/knowledge-uuid

# 3. Update progress
PUT /api/v1/users/student-uuid/knowledge/knowledge-uuid
{
  "progress": 75,
  "status": "learning"
}
```

### 3. Bulk Import
```bash
# 1. Import users
POST /api/v1/users/bulk
{
  "users": [
    {"name": "Student 1", "email": "s1@example.com", "age": 7},
    {"name": "Student 2", "email": "s2@example.com", "age": 8}
  ]
}

# 2. Import questions
POST /api/v1/questions/bulk
{
  "questions": [
    {
      "lesson_id": "lesson-uuid",
      "title": "Math Question",
      "content": "What is 2+2?",
      "correct_answer": "4",
      "difficulty": "dễ",
      "page": 10
    }
  ]
}

# 3. Bulk link knowledge
POST /api/v1/users/bulk/knowledge
{
  "links": [
    {
      "user_id": "user-uuid",
      "knowledge_id": "knowledge-uuid",
      "progress": 0
    }
  ]
}
```

---

## ❌ Common Errors

### 400 - Bad Request
```json
{
  "error": "Missing required fields: ['name', 'email']",
  "success": false
}
```

### 404 - Not Found
```json
{
  "error": "User not found",
  "success": false
}
```

### 409 - Conflict
```json
{
  "error": "Email already exists", 
  "success": false
}
```

### 500 - Server Error
```json
{
  "error": "Database connection failed",
  "success": false
}
```

---

## 📝 Field Reference

### User Fields
- `name` (required): Student name
- `email` (required): Unique email
- `age` (optional): Student age (default: 7)

### Question Fields
- `lesson_id` (required): Must exist in database
- `title` (required): Question title
- `content` (required): Question content
- `correct_answer` (required): Correct answer
- `difficulty` (required): `"dễ"`, `"trung bình"`, `"khó"`
- `page` (required): Page number
- `image_question` (optional): Question image URL
- `image_answer` (optional): Answer image URL

### Answer Fields
- `user_id` (required): Must exist in database
- `question_id` (required): Must exist in database
- `student_answer` (required): Student's answer
- `is_correct` (required): Boolean
- `start_time` (optional): ISO datetime
- `completion_time` (optional): ISO datetime
- `duration_seconds` (optional): Integer

### Knowledge Fields
- `name` (required): Knowledge name
- `subject` (required): Subject name
- `grade` (required): Grade level
- `description` (optional): Description
- `order` (optional): Sort order

### Progress Fields
- `progress` (optional): 0-100 integer
- `status` (optional): `"learning"`, `"completed"`, `"mastered"`, `"reviewing"`

---

*Last Updated: May 27, 2025*