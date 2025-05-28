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
User → Test → Question → TestAnswer (Test System)
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

## 🧪 Test System (New)

### Create Complete Test
Create a test with questions and answers in one API call.

```bash
POST /api/v1/tests/complete-simple
Content-Type: application/json

{
  "title": "Bài kiểm tra Toán đơn giản",
  "description": "Bài test cơ bản",
  "user_id": "511f5100-1c1a-4018-8ce1-ae3cbb0fcc9e",
  "duration_minutes": 30,
  "questions": [
    {
      "question": "2 + 3 bằng bao nhiêu?",
      "answer": "5",
      "image_question": "images/math1.png",
      "image_answer": "",
      "student_answer": "5",
      "is_correct": true,
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
      "is_correct": false,
      "points": 2,
      "difficulty": "medium",
      "duration_seconds": 45
    }
  ]
}
```

**Required fields**:
- `title`, `description`, `user_id`, `questions`
- **Per question**: `question`, `answer`, `student_answer`, `is_correct`

**Optional fields**:
- `duration_minutes` (default: 60)
- **Per question**: `image_question`, `image_answer`, `points` (default: 1), `difficulty` (default: "medium"), `duration_seconds` (default: 0)

**Response**: Complete test with questions, answers, and summary statistics.

### Get User Test History (Simple)
Get complete test history for a student with minimal structure.

```bash
GET /api/v1/users/{user_id}/test-history-minimal
```

**Example**:
```bash
GET /api/v1/users/511f5100-1c1a-4018-8ce1-ae3cbb0fcc9e/test-history-minimal
```

**Response structure**:
```json
{
  "user": {
    "id": "user-id",
    "name": "Student Name",
    "email": "email@example.com"
  },
  "test_history": [
    {
      "test": {
        "id": "test-id",
        "title": "Test Title",
        "description": "Test Description",
        "start_time": "2024-01-01T10:00:00",
        "end_time": "2024-01-01T10:30:00",
        "status": "completed",
        "created_at": "2024-01-01T10:00:00"
      },
      "questions_and_answers": [
        {
          "question": {
            "id": "q1",
            "content": "Question content",
            "correct_answer": "Correct answer",
            "image_question": "images/q1.png",
            "image_answer": "images/a1.png",
            "difficulty": "easy"
          },
          "answer": {
            "id": "a1",
            "student_answer": "Student answer",
            "is_correct": true,
            "answered_at": "2024-01-01T10:05:00",
            "duration_seconds": 45
          }
        }
      ],
      "summary": {
        "total_questions": 5,
        "correct_answers": 3,
        "wrong_answers": 2,
        "accuracy_percentage": 60.0
      }
    }
  ],
  "total_tests": 1,
  "success": true
}
```

### Get Test Details (Simple)
Get detailed information for a specific test.

```bash
GET /api/v1/tests/{test_id}/details-simple
```

**Example**:
```bash
GET /api/v1/tests/test-uuid-here/details-simple
```

**Response**: Detailed test info with questions, answers, summary statistics, and difficulty analysis.

### Search Tests
Search tests with various criteria.

```bash
GET /api/v1/tests/search?user_id={user_id}&title={search_term}&from_date={date}&to_date={date}&min_score={score}&max_score={score}
```

**Parameters**:
- `user_id`: Filter by specific user
- `title`: Search in test titles
- `from_date`: Start date (YYYY-MM-DD)
- `to_date`: End date (YYYY-MM-DD)  
- `min_score`: Minimum accuracy percentage
- `max_score`: Maximum accuracy percentage

**Example**:
```bash
GET /api/v1/tests/search?user_id=511f5100-1c1a-4018-8ce1-ae3cbb0fcc9e&title=Toán&min_score=60
```

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

## 🚀 Quick Start Examples

### 1. Complete Test Workflow (New)
```bash
# 1. Create a simple test with questions and answers
POST /api/v1/tests/complete-simple
{
  "title": "Bài kiểm tra Toán",
  "description": "Test cơ bản",
  "user_id": "student-uuid",
  "questions": [
    {
      "question": "2 + 3 = ?",
      "answer": "5",
      "student_answer": "5",
      "is_correct": true,
      "points": 1
    },
    {
      "question": "Đếm quả táo?",
      "answer": "4 quả",
      "image_question": "images/apples.jpg",
      "student_answer": "3 quả",
      "is_correct": false,
      "points": 2
    }
  ]
}

# 2. Get student's test history
GET /api/v1/users/student-uuid/test-history-minimal

# 3. Get specific test details
GET /api/v1/tests/test-uuid/details-simple

# 4. Search tests
GET /api/v1/tests/search?user_id=student-uuid&min_score=60
```

### 2. Complete Learning Workflow
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

### 3. Knowledge Management
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

### 4. Bulk Import
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

### Test Fields (New)
- `title` (required): Test title
- `description` (required): Test description
- `user_id` (required): Student ID
- `duration_minutes` (optional): Test duration (default: 60)
- `questions` (required): Array of questions

### Test Question Fields (New)
- `question` (required): Question content
- `answer` (required): Correct answer
- `student_answer` (required): Student's response
- `is_correct` (required): Boolean
- `image_question` (optional): Question image URL
- `image_answer` (optional): Answer image URL
- `points` (optional): Points value (default: 1)
- `difficulty` (optional): Difficulty level (default: "medium")
- `duration_seconds` (optional): Time taken (default: 0)

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

## 🏗️ Test System Architecture

### Relationship Structure
```
User -[:TOOK]-> Test -[:CONTAINS_QUESTION]-> Question -[:HAS_ANSWER]-> TestAnswer
```

### Key Features
- **Simple Test Creation**: One API call creates test + questions + answers
- **Minimal Fields**: Only essential fields required
- **Image Support**: Questions and answers can have images
- **Complete History**: Easy access to all test data
- **Flexible Search**: Search tests by multiple criteria
- **Clean Structure**: No complex hierarchies, just question → answer

### Differences from Regular Q&A System
- **Test System**: Groups questions into tests, tracks test completion
- **Regular Q&A**: Individual questions linked to lessons/chapters
- **Use Test System**: For assessments, quizzes, exams
- **Use Regular Q&A**: For practice, learning content exploration

---

*Last Updated: May 28, 2025*