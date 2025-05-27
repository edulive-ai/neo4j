# Education API - Complete Documentation

## 📋 Overview

**Neo4j Educational API** - A comprehensive REST API for managing educational content with hierarchical structure and user knowledge tracking.

- **Base URL**: `http://localhost:5000`
- **Version**: v1
- **Database**: Neo4j Graph Database
- **Framework**: Flask with CORS support

## 🏗️ Data Structure

### Hierarchy Model
```
Subject → TypeBook → Chapter → Lesson → Question
```

### Node Types
- **Subject**: Top-level educational subjects (e.g., "Toán", "Tiếng Việt")
- **TypeBook**: Course materials (e.g., "Sách Giáo Khoa Toán Lớp 1")
- **Chapter**: Learning chapters (e.g., "Học kì I")
- **Lesson**: Individual lessons within chapters
- **Question**: Educational questions linked to lessons
- **User**: Students/learners in the system
- **Answer**: Student responses to questions
- **Knowledge**: Individual knowledge points students can learn

### Relationships
```cypher
(User)-[:ANSWERED]->(Answer)-[:ANSWERS_QUESTION]->(Question)
(Question)-[:BELONGS_TO_LESSON]->(Lesson)
(Lesson)-[:BELONGS_TO_CHAPTER]->(Chapter)
(Chapter)-[:BELONGS_TO_TYPE_BOOK]->(TypeBook)
(TypeBook)-[:BELONGS_TO_SUBJECT]->(Subject)
(User)-[:LEARNED]->(Knowledge)
```

---

## 🔌 API Endpoints

### 🏥 Health Check

#### `GET /api/v1/health`
Check API and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "success": true
}
```

---

### 📚 Hierarchy Management

#### `GET /api/v1/subjects`
Get all subjects in the system.

**Response:**
```json
{
  "subjects": [
    {
      "id": "uuid",
      "name": "Toán",
      "description": "Môn Toán học",
      "createdAt": "2025-05-27T10:00:00.000000",
      "updatedAt": "2025-05-27T10:00:00.000000"
    }
  ],
  "count": 1,
  "success": true
}
```

#### `GET /api/v1/typebooks`
Get typebooks with optional subject filtering.

**Query Parameters:**
- `subject_id` (optional): Filter by specific subject

**Response:**
```json
{
  "typebooks": [
    {
      "id": "uuid",
      "name": "Sách Giáo Khoa Toán Lớp 1",
      "description": "Sách giáo khoa môn Toán lớp 1",
      "subject_name": "Toán",
      "createdAt": "2025-05-27T10:00:00.000000"
    }
  ],
  "count": 1,
  "success": true
}
```

#### `GET /api/v1/chapters`
Get chapters with optional typebook filtering.

**Query Parameters:**
- `typebook_id` (optional): Filter by specific typebook

**Response:**
```json
{
  "chapters": [
    {
      "id": "uuid",
      "name": "Học kì I",
      "description": "Chương trình học kì I",
      "order": 1,
      "typebook_name": "Sách Giáo Khoa Toán Lớp 1"
    }
  ],
  "count": 1,
  "success": true
}
```

#### `GET /api/v1/lessons`
Get lessons with optional chapter filtering.

**Query Parameters:**
- `chapter_id` (optional): Filter by specific chapter

**Response:**
```json
{
  "lessons": [
    {
      "id": "uuid",
      "name": "Trên - Dưới, Phải - Trái, Trước - Sau, Ở giữa",
      "description": "Học về vị trí không gian cơ bản",
      "order": 1,
      "chapter_name": "Học kì I"
    }
  ],
  "count": 1,
  "success": true
}
```

---

### 👥 User Management

#### `GET /api/v1/users`
Get all users in the system.

**Response:**
```json
{
  "users": [
    {
      "id": "uuid",
      "name": "Nguyễn Văn A",
      "email": "student@example.com",
      "age": 7,
      "createdAt": "2025-05-27T10:00:00.000000",
      "updatedAt": "2025-05-27T10:00:00.000000"
    }
  ],
  "count": 1,
  "success": true
}
```

#### `POST /api/v1/users`
Create a new user.

**Request Body:**
```json
{
  "name": "Nguyễn Văn A",
  "email": "student@example.com",
  "age": 7
}
```

**Response:**
```json
{
  "message": "User created",
  "user": {
    "id": "generated-uuid",
    "name": "Nguyễn Văn A",
    "email": "student@example.com",
    "age": 7,
    "createdAt": "2025-05-27T10:00:00.000000",
    "updatedAt": "2025-05-27T10:00:00.000000"
  },
  "success": true
}
```

#### `POST /api/v1/users/bulk`
Bulk import multiple users with optimization.

**Request Body:**
```json
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

**Response:**
```json
{
  "message": "2 users imported successfully (optimized)",
  "created_users": [...],
  "total_processed": 2,
  "total_created": 2,
  "total_errors": 0,
  "errors": [],
  "success": true
}
```

---

### ❓ Question Management

#### `GET /api/v1/questions`
Get questions with full hierarchy context.

**Query Parameters:**
- `lesson_id` (optional): Filter by specific lesson
- `chapter_id` (optional): Filter by specific chapter

**Response:**
```json
{
  "questions": [
    {
      "id": "uuid",
      "title": "Bài 1 trang 7 sách giáo khoa toán lớp 1",
      "content": "Dùng các từ: trên, dưới, trái, phải để nói về bức tranh?",
      "correct_answer": "Bạn Lan đang ngồi ở giữa bàn học...",
      "image_question": "images/bai1-trang7-sgk.png",
      "image_answer": "",
      "difficulty": "dễ",
      "page": 7,
      "lesson_name": "Trên - Dưới, Phải - Trái",
      "chapter_name": "Học kì I",
      "typebook_name": "Sách Giáo Khoa Toán Lớp 1",
      "subject_name": "Toán"
    }
  ],
  "count": 1,
  "success": true
}
```

#### `POST /api/v1/questions/bulk`
Bulk import questions with lesson relationships.

**Request Body:**
```json
{
  "questions": [
    {
      "lesson_id": "existing-lesson-uuid",
      "title": "Câu hỏi về số học",
      "content": "2 + 2 = ?",
      "correct_answer": "4",
      "difficulty": "dễ",
      "page": 15,
      "image_question": "optional-image-url"
    }
  ],
  "batch_size": 500
}
```

**Response:**
```json
{
  "message": "1 questions imported with relationships (optimized)",
  "created_questions": [...],
  "total_processed": 1,
  "total_created": 1,
  "total_errors": 0,
  "errors": [],
  "performance": {
    "batch_size": 500,
    "batches_processed": 1
  },
  "success": true
}
```

---

### ✅ Answer Management

#### `POST /api/v1/answers/bulk`
Bulk import student answers with dual relationships.

**Request Body:**
```json
{
  "answers": [
    {
      "user_id": "student-uuid",
      "question_id": "question-uuid", 
      "student_answer": "Em thấy có 4",
      "is_correct": true,
      "start_time": "2025-05-27T10:00:00.000000",
      "completion_time": "2025-05-27T10:02:00.000000",
      "duration_seconds": 120
    }
  ],
  "batch_size": 500
}
```

**Response:**
```json
{
  "message": "1 answers imported with dual relationships (optimized)",
  "created_answers": [...],
  "total_processed": 1,
  "total_created": 1,
  "total_errors": 0,
  "errors": [],
  "performance": {
    "batch_size": 500,
    "batches_processed": 1
  },
  "success": true
}
```

---

### 🧠 Knowledge Management

#### `GET /api/v1/knowledge`
Get all knowledge nodes with optional filtering.

**Query Parameters:**
- `subject` (optional): Filter by subject (e.g., "Toán")
- `grade` (optional): Filter by grade (e.g., "Lớp 1")

**Response:**
```json
{
  "knowledge": [
    {
      "id": "uuid",
      "name": "Trên - Dưới, Phải - Trái, Trước - Sau, Ở giữa",
      "description": "Kiến thức về: Trên - Dưới, Phải - Trái, Trước - Sau, Ở giữa",
      "order": 1,
      "subject": "Toán",
      "grade": "Lớp 1",
      "createdAt": "2025-05-27T10:00:00.000000",
      "updatedAt": "2025-05-27T10:00:00.000000"
    }
  ],
  "count": 1,
  "filters": {
    "subject": "Toán",
    "grade": "Lớp 1"
  },
  "success": true
}
```

#### `POST /api/v1/knowledge`
Create a new knowledge node.

**Request Body:**
```json
{
  "name": "Phép cộng cơ bản",
  "description": "Kiến thức về phép cộng trong phạm vi 10",
  "order": 15,
  "subject": "Toán",
  "grade": "Lớp 1"
}
```

**Response:**
```json
{
  "message": "Knowledge created successfully",
  "knowledge": {
    "id": "generated-uuid",
    "name": "Phép cộng cơ bản",
    "description": "Kiến thức về phép cộng trong phạm vi 10",
    "order": 15,
    "subject": "Toán",
    "grade": "Lớp 1",
    "createdAt": "2025-05-27T10:00:00.000000",
    "updatedAt": "2025-05-27T10:00:00.000000"
  },
  "success": true
}
```

---

### 🔗 User-Knowledge Relationships

#### `POST /api/v1/users/{user_id}/knowledge/{knowledge_id}`
Link a user to specific knowledge with timestamp.

**Response:**
```json
{
  "message": "User linked to knowledge successfully",
  "link": {
    "user_name": "Nguyễn Văn A",
    "knowledge_name": "Trên - Dưới, Phải - Trái",
    "relationship": {
      "linkedAt": "2025-05-27T10:00:00.000000",
      "status": "learning",
      "progress": 0,
      "createdAt": "2025-05-27T10:00:00.000000",
      "updatedAt": "2025-05-27T10:00:00.000000"
    },
    "knowledge_info": {...}
  },
  "success": true
}
```

#### `GET /api/v1/users/{user_id}/knowledge`
Get all knowledge linked to a specific user.

**Response:**
```json
{
  "user": {
    "id": "user-uuid",
    "name": "Nguyễn Văn A",
    "email": "student@example.com"
  },
  "knowledge_list": [
    {
      "knowledge": {
        "id": "knowledge-uuid",
        "name": "Trên - Dưới, Phải - Trái",
        "subject": "Toán",
        "grade": "Lớp 1"
      },
      "relationship": {
        "linkedAt": "2025-05-27T10:00:00.000000",
        "status": "learning",
        "progress": 75,
        "updatedAt": "2025-05-27T10:30:00.000000"
      },
      "linked_date": "2025-05-27",
      "linked_time": "10:00:00"
    }
  ],
  "total_knowledge": 1,
  "success": true
}
```

#### `GET /api/v1/knowledge/{knowledge_id}/users`
Get all users linked to a specific knowledge.

**Response:**
```json
{
  "knowledge": {
    "id": "knowledge-uuid",
    "name": "Trên - Dưới, Phải - Trái",
    "subject": "Toán",
    "grade": "Lớp 1"
  },
  "users_list": [
    {
      "user": {
        "id": "user-uuid",
        "name": "Nguyễn Văn A",
        "email": "student@example.com"
      },
      "relationship": {
        "linkedAt": "2025-05-27T10:00:00.000000",
        "status": "learning",
        "progress": 75
      },
      "linked_date": "2025-05-27",
      "linked_time": "10:00:00"
    }
  ],
  "total_users": 1,
  "success": true
}
```

#### `PUT /api/v1/users/{user_id}/knowledge/{knowledge_id}`
Update user's progress on specific knowledge.

**Request Body:**
```json
{
  "progress": 85,
  "status": "completed"
}
```

**Response:**
```json
{
  "message": "User knowledge progress updated",
  "update": {
    "user_name": "Nguyễn Văn A",
    "knowledge_name": "Trên - Dưới, Phải - Trái",
    "relationship": {
      "linkedAt": "2025-05-27T10:00:00.000000",
      "status": "completed",
      "progress": 85,
      "updatedAt": "2025-05-27T11:00:00.000000"
    }
  },
  "success": true
}
```

#### `DELETE /api/v1/users/{user_id}/knowledge/{knowledge_id}`
Remove link between user and knowledge.

**Response:**
```json
{
  "message": "User unlinked from knowledge successfully",
  "unlinked": {
    "user_name": "Nguyễn Văn A",
    "knowledge_name": "Trên - Dưới, Phải - Trái"
  },
  "success": true
}
```

#### `POST /api/v1/users/bulk/knowledge`
Bulk link multiple users to multiple knowledge nodes.

**Request Body:**
```json
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

**Response:**
```json
{
  "message": "2 user-knowledge links created successfully",
  "created_links": [...],
  "total_processed": 2,
  "total_created": 2,
  "total_errors": 0,
  "errors": [],
  "success": true
}
```

---

### 📊 Analytics & Insights

#### `GET /api/v1/users-knowledge/analytics`
Get comprehensive analytics for user-knowledge relationships.

**Response:**
```json
{
  "overall_stats": {
    "total_users_learning": 150,
    "total_knowledge_being_learned": 43,
    "total_relationships": 500,
    "avg_progress": 67.5
  },
  "progress_distribution": {
    "Not Started": 50,
    "Beginner (1-24%)": 75,
    "Intermediate (25-49%)": 100,
    "Advanced (50-74%)": 150,
    "Near Complete (75-99%)": 75,
    "Completed (100%)": 50
  },
  "status_distribution": {
    "learning": 300,
    "completed": 150,
    "mastered": 30,
    "reviewing": 20
  },
  "most_popular_knowledge": [
    {
      "knowledge_name": "Các số 1, 2, 3",
      "subject": "Toán",
      "grade": "Lớp 1",
      "learner_count": 120,
      "avg_progress": 85.5
    }
  ],
  "most_active_users": [
    {
      "user_name": "Nguyễn Văn A",
      "user_email": "student@example.com",
      "knowledge_count": 25,
      "avg_progress": 78.5,
      "latest_activity": "2025-05-27T10:00:00.000000"
    }
  ],
  "success": true
}
```

---

### 🎓 Student Detailed Analytics

#### `GET /api/v1/students/{user_id}/detailed`
Get comprehensive detailed information for a single student.

**Response:**
```json
{
  "student": {
    "id": "user-uuid",
    "name": "Nguyễn Văn A",
    "email": "student@example.com",
    "age": 7
  },
  "detailed_answers": [
    {
      "answer_id": "answer-uuid",
      "student_answer": "Em thấy có 4",
      "is_correct": true,
      "start_time": "2025-05-27T10:00:00.000000",
      "completion_time": "2025-05-27T10:02:00.000000",
      "duration_seconds": 120,
      "question": {
        "id": "question-uuid",
        "title": "Bài tập đếm số",
        "content": "Đếm số táo trong hình",
        "correct_answer": "4",
        "difficulty": "dễ",
        "page": 15
      },
      "lesson": {
        "id": "lesson-uuid",
        "name": "Các số 1, 2, 3",
        "order": 3
      },
      "chapter": {
        "id": "chapter-uuid",
        "name": "Học kì I",
        "order": 1
      },
      "typebook": {
        "id": "typebook-uuid",
        "name": "Sách Giáo Khoa Toán Lớp 1"
      },
      "subject": {
        "id": "subject-uuid",
        "name": "Toán"
      }
    }
  ],
  "learning_progress": [
    {
      "subject": {
        "id": "subject-uuid",
        "name": "Toán"
      },
      "typebooks": [...],
      "chapters": [...],
      "latest_activity": "2025-05-27T10:02:00.000000",
      "first_activity": "2025-05-20T09:00:00.000000"
    }
  ],
  "recent_mistakes": [
    {
      "answer_id": "answer-uuid",
      "student_answer": "Em trả lời sai",
      "completion_time": "2025-05-27T09:30:00.000000",
      "question": {
        "id": "question-uuid",
        "title": "Câu hỏi khó",
        "content": "Nội dung câu hỏi",
        "correct_answer": "Đáp án đúng",
        "difficulty": "khó",
        "page": 20
      },
      "lesson_name": "Phép cộng nâng cao",
      "chapter_name": "Học kì I"
    }
  ],
  "study_dates": ["2025-05-27", "2025-05-26", "2025-05-25"],
  "summary_counts": {
    "total_answers": 50,
    "correct_answers": 42,
    "subjects_studied": 2,
    "recent_mistakes": 3
  },
  "has_data": true,
  "success": true
}
```

#### `GET /api/v1/students/detailed`
Get detailed information for multiple students with filtering.

**Query Parameters:**
- `user_ids`: Comma-separated list of user IDs
- `subject_id`: Filter by specific subject
- `chapter_id`: Filter by specific chapter  
- `lesson_id`: Filter by specific lesson
- `limit`: Maximum number of students to return (default: 20)

**Response:**
```json
{
  "students": [
    {
      "student": {
        "id": "user-uuid",
        "name": "Nguyễn Văn A",
        "email": "student@example.com",
        "age": 7,
        "createdAt": "2025-05-20T09:00:00.000000"
      },
      "all_answers": [...],
      "recent_answers": [...],
      "subjects_studied": ["Toán", "Tiếng Việt"],
      "answers_by_subject": {
        "Toán": [...],
        "Tiếng Việt": [...]
      },
      "difficulty_performance": {
        "dễ": {"total": 20, "correct": 18},
        "trung bình": {"total": 15, "correct": 12},
        "khó": {"total": 5, "correct": 3}
      },
      "metrics": {
        "total_answers": 40,
        "correct_answers": 33,
        "accuracy_rate": 82.5,
        "avg_duration": 95,
        "subjects_count": 2
      }
    }
  ],
  "filter_info": {
    "applied_filters": {
      "user_ids": ["user1", "user2"],
      "subject_id": "math-subject-id",
      "chapter_id": null,
      "lesson_id": null,
      "limit": 20
    },
    "total_students": 2
  },
  "success": true
}
```

---

### 🌳 Tree Structure & Export

#### `GET /api/v1/tree`
Get complete hierarchical tree structure with all IDs.

**Query Parameters:**
- `include_users`: Include users list (default: true)
- `include_questions`: Include questions in lessons (default: true)

**Response:**
```json
{
  "tree_structure": [
    {
      "id": "subject-uuid",
      "name": "Toán",
      "type": "subject",
      "typebooks": [
        {
          "id": "typebook-uuid",
          "name": "Sách Giáo Khoa Toán Lớp 1",
          "type": "typebook",
          "chapters": [
            {
              "id": "chapter-uuid",
              "name": "Học kì I", 
              "order": 1,
              "type": "chapter",
              "lessons": [
                {
                  "id": "lesson-uuid",
                  "name": "Trên - Dưới, Phải - Trái",
                  "order": 1,
                  "type": "lesson",
                  "questions": [
                    {
                      "id": "question-uuid",
                      "title": "Bài 1 trang 7",
                      "page": 7
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "users": [
    {
      "id": "user-uuid",
      "name": "Nguyễn Văn A",
      "email": "student@example.com"
    }
  ],
  "summary": {
    "total_subjects": 1,
    "total_users": 1,
    "include_users": true,
    "include_questions": true
  },
  "success": true
}
```

#### `GET /api/v1/export`
Export all data with full hierarchy context.

**Response:**
```json
{
  "users": [...],
  "questions": [...],
  "answers": [...],
  "summary": {
    "total_users": 150,
    "total_questions": 500,
    "total_answers": 2000
  },
  "success": true
}
```

---

## 🛠️ Configuration

### Environment Variables
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
PORT=5000
DEBUG=False
```

### Dependencies
```bash
pip install flask flask-cors neo4j logging
```

---

## 🔄 Workflow Examples

### 1. **Complete Learning Workflow**
```bash
# 1. Get available subjects
GET /api/v1/subjects

# 2. Get lessons for specific chapter  
GET /api/v1/lessons?chapter_id=chapter-uuid

# 3. Get questions for lesson
GET /api/v1/questions?lesson_id=lesson-uuid

# 4. Submit student answer
POST /api/v1/answers/bulk
{
  "answers": [{
    "user_id": "student-uuid",
    "question_id": "question-uuid", 
    "student_answer": "Student response",
    "is_correct": true,
    "duration_seconds": 120
  }]
}

# 5. Check student progress
GET /api/v1/students/student-uuid/detailed
```

### 2. **Knowledge Management Workflow**
```bash
# 1. Create/Get knowledge nodes
GET /api/v1/knowledge?subject=Toán&grade=Lớp 1

# 2. Link student to knowledge
POST /api/v1/users/student-uuid/knowledge/knowledge-uuid

# 3. Update learning progress
PUT /api/v1/users/student-uuid/knowledge/knowledge-uuid
{
  "progress": 75,
  "status": "learning"
}

# 4. View student's knowledge
GET /api/v1/users/student-uuid/knowledge

# 5. Analytics overview
GET /api/v1/users-knowledge/analytics
```

### 3. **Bulk Import Workflow**
```bash
# 1. Import users
POST /api/v1/users/bulk
{
  "users": [
    {"name": "Student 1", "email": "s1@example.com", "age": 7},
    {"name": "Student 2", "email": "s2@example.com", "age": 8}
  ]
}

# 2. Import questions (requires existing lessons)
POST /api/v1/questions/bulk
{
  "questions": [
    {
      "lesson_id": "existing-lesson-uuid",
      "title": "Math Question 1",
      "content": "What is 2+2?",
      "correct_answer": "4",
      "difficulty": "dễ",
      "page": 10
    }
  ]
}

# 3. Import answers
POST /api/v1/answers/bulk
{
  "answers": [
    {
      "user_id": "student-uuid",
      "question_id": "question-uuid",
      "student_answer": "4",
      "is_correct": true,
      "duration_seconds": 60
    }
  ]
}

# 4. Bulk link knowledge
POST /api/v1/users/bulk/knowledge
{
  "links": [
    {
      "user_id": "student-uuid",
      "knowledge_id": "knowledge-uuid",
      "status": "learning",
      "progress": 0
    }
  ]
}
```

---

## ❌ Error Handling

### Standard Error Response
```json
{
  "error": "Error description",
  "success": false
}
```

### Common HTTP Status Codes
- **200**: Success
- **201**: Created successfully
- **400**: Bad Request (validation error)
- **404**: Resource not found
- **409**: Conflict (duplicate resource)
- **500**: Internal Server Error

### Validation Errors
```json
{
  "error": "Missing required fields: ['name', 'email']",
  "success": false
}
```

### Bulk Import Errors
```json
{
  "message": "5 users imported successfully (optimized)",
  "created_users": [...],
  "total_processed": 7,
  "total_created": 5,
  "total_errors": 2,
  "errors": [
    "User 3: Missing name or email",
    "User 5: Email already exists"
  ],
  "success": true
}
```

---

## 🔧 Performance Features

### Optimized Bulk Operations
- **Batch Processing**: Configurable batch sizes for large imports
- **Transaction Management**: Atomic operations with rollback capability
- **Relationship Validation**: Efficient existence checks before creation
- **Error Isolation**: Continue processing valid records despite individual errors

### Query Optimizations
- **Index Usage**: Leverages Neo4j indexes for fast lookups
- **Selective Loading**: Optional data inclusion to reduce response size
- **Pagination Support**: Limit parameters for large result sets
- **Efficient Aggregations**: Optimized analytics queries

---

## 🎯 Random Questions API

### `GET /api/v1/questions/random`
Get random questions with comprehensive filtering options.

**Query Parameters:**
- `count` (int, default: 10): Number of questions (max 100)
- `subject_id` (string): Filter by specific subject
- `typebook_id` (string): Filter by specific typebook
- `chapter_id` (string): Filter by specific chapter
- `lesson_id` (string): Filter by specific lesson
- `difficulty` (string): Filter by difficulty level ("dễ", "trung bình", "khó")
- `page_min` (int): Minimum page number
- `page_max` (int): Maximum page number
- `include_answered` (boolean, default: true): Include questions already answered
- `user_id` (string): User ID to exclude answered questions (when include_answered=false)

**Example Request:**
```bash
GET /api/v1/questions/random?count=5&difficulty=dễ&subject_id=math-uuid&exclude_answered=true&user_id=student-uuid
```

**Response:**
```json
{
  "questions": [
    {
      "question": {
        "id": "question-uuid",
        "title": "Bài tập đếm số",
        "content": "Đếm số táo trong hình",
        "correct_answer": "4",
        "image_question": "images/counting.png",
        "image_answer": "",
        "difficulty": "dễ",
        "page": 15,
        "createdAt": "2025-05-27T10:00:00.000000"
      },
      "hierarchy": {
        "subject": {"id": "subject-uuid", "name": "Toán"},
        "typebook": {"id": "typebook-uuid", "name": "SGK Toán Lớp 1"},
        "chapter": {"id": "chapter-uuid", "name": "Học kì I", "order": 1},
        "lesson": {"id": "lesson-uuid", "name": "Các số 1, 2, 3", "order": 3}
      },
      "full_path": "Toán > SGK Toán Lớp 1 > Học kì I > Các số 1, 2, 3"
    }
  ],
  "count_returned": 5,
  "count_requested": 5,
  "total_available": 150,
  "filters_applied": {
    "subject_id": "math-uuid",
    "typebook_id": null,
    "chapter_id": null,
    "lesson_id": null,
    "difficulty": "dễ",
    "page_range": null,
    "exclude_answered_for_user": "student-uuid"
  },
  "success": true
}
```

### `GET /api/v1/questions/random/quiz`
Generate a balanced random quiz with multiple difficulty levels.

**Query Parameters:**
- `total_questions` (int, default: 15): Total number of questions in quiz
- `easy_count` (int, default: 5): Number of easy questions
- `medium_count` (int, default: 5): Number of medium questions
- `hard_count` (int, default: 5): Number of hard questions
- `subject_id` (string): Filter by specific subject
- `chapter_id` (string): Filter by specific chapter
- `user_id` (string): User ID for personalization
- `exclude_answered` (boolean, default: true): Exclude already answered questions

**Example Request:**
```bash
GET /api/v1/questions/random/quiz?total_questions=12&easy_count=4&medium_count=4&hard_count=4&subject_id=math-uuid&user_id=student-uuid
```

**Response:**
```json
{
  "quiz": [
    {
      "question": {
        "id": "question-uuid",
        "title": "Phép cộng đơn giản",
        "content": "2 + 3 = ?",
        "correct_answer": "5",
        "difficulty": "dễ",
        "page": 20
      },
      "hierarchy": {
        "subject": {"id": "subject-uuid", "name": "Toán"},
        "typebook": {"id": "typebook-uuid", "name": "SGK Toán Lớp 1"},
        "chapter": {"id": "chapter-uuid", "name": "Học kì I"},
        "lesson": {"id": "lesson-uuid", "name": "Phép cộng trong phạm vi 6"}
      }
    }
  ],
  "quiz_info": {
    "total_questions": 12,
    "requested_distribution": {
      "easy": 4,
      "medium": 4,
      "hard": 4
    },
    "actual_distribution": {
      "easy": 4,
      "medium": 4,
      "hard": 4
    }
  },
  "filters_applied": {
    "subject_id": "math-uuid",
    "chapter_id": null,
    "exclude_answered_for_user": "student-uuid"
  },
  "success": true
}
```

### `GET /api/v1/questions/random/by-subject`
Get random questions distributed across all subjects.

**Query Parameters:**
- `count` (int, default: 20): Total number of questions
- `questions_per_subject` (int, default: 0): Questions per subject (0 = auto distribute)
- `user_id` (string): User ID for personalization
- `exclude_answered` (boolean, default: true): Exclude answered questions

**Response:**
```json
{
  "questions": [
    {
      "question": {
        "id": "question-uuid",
        "title": "Câu hỏi Toán",
        "content": "Nội dung câu hỏi",
        "correct_answer": "Đáp án",
        "difficulty": "dễ",
        "page": 10
      },
      "hierarchy": {
        "subject": {"id": "subject-uuid", "name": "Toán"},
        "typebook": {"id": "typebook-uuid", "name": "SGK Toán Lớp 1"},
        "chapter": {"id": "chapter-uuid", "name": "Học kì I"},
        "lesson": {"id": "lesson-uuid", "name": "Các số 1, 2, 3"}
      }
    }
  ],
  "distribution": {
    "Toán": 10,
    "Tiếng Việt": 7,
    "Tự nhiên xã hội": 3
  },
  "total_returned": 20,
  "total_requested": 20,
  "questions_per_subject_requested": 0,
  "subjects_available": 3,
  "success": true
}
```

### `GET /api/v1/questions/random/stats`
Get statistics for random question generation to help with quiz planning.

**Response:**
```json
{
  "overall_stats": {
    "total_questions": 500,
    "total_subjects": 3,
    "total_typebooks": 5,
    "total_chapters": 15,
    "total_lessons": 50
  },
  "difficulty_distribution": {
    "dễ": 200,
    "trung bình": 200,
    "khó": 100
  },
  "subject_distribution": {
    "Toán": 250,
    "Tiếng Việt": 150,
    "Tự nhiên xã hội": 100
  },
  "lesson_stats": {
    "lessons_with_questions": 50,
    "total_questions": 500,
    "avg_questions_per_lesson": 10
  },
  "recommendations": {
    "max_recommended_random_count": 50,
    "good_quiz_size": 15,
    "available_difficulties": ["dễ", "trung bình", "khó"],
    "subjects_available": ["Toán", "Tiếng Việt", "Tự nhiên xã hội"]
  },
  "success": true
}
```

---

## 📈 Advanced Analytics

### `GET /api/v1/analytics/hierarchy`
Get detailed analytics broken down by educational hierarchy.

**Response:**
```json
{
  "hierarchy_analytics": [
    {
      "subject_name": "Toán",
      "typebook_name": "SGK Toán Lớp 1",
      "chapter_name": "Học kì I",
      "lesson_name": "Các số 1, 2, 3",
      "chapter_order": 1,
      "lesson_order": 3,
      "total_questions": 15,
      "total_answers": 450,
      "correct_answers": 380,
      "accuracy_percentage": 84.44
    }
  ],
  "success": true
}
```

### `GET /api/v1/analytics/user/{user_id}`
Get comprehensive performance analytics for a specific user.

**Response:**
```json
{
  "user": {
    "id": "user-uuid",
    "name": "Nguyễn Văn A",
    "email": "student@example.com",
    "age": 7
  },
  "overall_stats": {
    "total_answers": 125,
    "correct_answers": 105,
    "accuracy_percentage": 84.0,
    "avg_duration": 95
  },
  "performance_by_hierarchy": [
    {
      "subject_name": "Toán",
      "typebook_name": "SGK Toán Lớp 1",
      "chapter_name": "Học kì I",
      "lesson_name": "Các số 1, 2, 3",
      "chapter_order": 1,
      "lesson_order": 3,
      "total_answers": 25,
      "correct_answers": 22,
      "accuracy_percentage": 88.0,
      "avg_duration": 85
    }
  ],
  "success": true
}
```

### `GET /api/v1/analytics/summary`
Get high-level system analytics and insights.

**Response:**
```json
{
  "summary": {
    "total_subjects": 3,
    "total_typebooks": 5,
    "total_chapters": 15,
    "total_lessons": 50,
    "total_questions": 500,
    "total_users": 150,
    "total_answers": 5000,
    "overall_accuracy": 78.5
  },
  "top_users": [
    {
      "user_name": "Nguyễn Văn A",
      "user_email": "student1@example.com",
      "total_answers": 125,
      "correct_answers": 105,
      "accuracy_percentage": 84.0
    }
  ],
  "difficulty_breakdown": [
    {
      "difficulty": "dễ",
      "question_count": 200,
      "answer_count": 2000,
      "correct_count": 1750,
      "accuracy_percentage": 87.5
    },
    {
      "difficulty": "trung bình",
      "question_count": 200,
      "answer_count": 2000,
      "correct_count": 1500,
      "accuracy_percentage": 75.0
    },
    {
      "difficulty": "khó",
      "question_count": 100,
      "answer_count": 1000,
      "correct_count": 650,
      "accuracy_percentage": 65.0
    }
  ],
  "success": true
}
```

### `GET /api/v1/analytics/subject/{subject_id}`
Get detailed analytics for a specific subject.

**Response:**
```json
{
  "subject": {
    "id": "subject-uuid",
    "name": "Toán",
    "description": "Môn Toán học"
  },
  "typebook_breakdown": [
    {
      "typebook_name": "SGK Toán Lớp 1",
      "chapter_count": 5,
      "lesson_count": 25,
      "question_count": 250,
      "answer_count": 2500,
      "correct_count": 2000,
      "accuracy_percentage": 80.0
    }
  ],
  "user_performance": [
    {
      "user_name": "Nguyễn Văn A",
      "user_email": "student1@example.com",
      "answers_in_subject": 60,
      "correct_in_subject": 52,
      "accuracy_percentage": 86.67,
      "avg_duration": 90
    }
  ],
  "success": true
}
```

---

## 🔍 Extended Student Analytics

### `GET /api/v1/students/answers-history`
Get detailed answer history with comprehensive filtering.

**Query Parameters:**
- `user_id` (string): Specific user ID
- `from_date` (string): Start date (ISO format: 2024-01-01)
- `to_date` (string): End date (ISO format: 2024-12-31)
- `difficulty` (string): Filter by question difficulty
- `is_correct` (string): Filter by correctness ("true", "false")
- `limit` (int, default: 100): Maximum records to return

**Example Request:**
```bash
GET /api/v1/students/answers-history?user_id=student-uuid&from_date=2025-05-01&to_date=2025-05-31&difficulty=dễ&is_correct=false&limit=20
```

**Response:**
```json
{
  "answer_history": [
    {
      "student_name": "Nguyễn Văn A",
      "student_email": "student@example.com",
      "answer_detail": {
        "id": "answer-uuid",
        "student_answer": "Em trả lời sai",
        "is_correct": false,
        "start_time": "2025-05-27T10:00:00.000000",
        "completion_time": "2025-05-27T10:02:30.000000",
        "duration_seconds": 150
      },
      "question_detail": {
        "id": "question-uuid",
        "title": "Phép cộng đơn giản",
        "content": "3 + 2 = ?",
        "correct_answer": "5",
        "difficulty": "dễ",
        "page": 25,
        "image_question": "images/addition.png",
        "image_answer": ""
      },
      "hierarchy_path": {
        "subject": {"id": "subject-uuid", "name": "Toán"},
        "typebook": {"id": "typebook-uuid", "name": "SGK Toán Lớp 1"},
        "chapter": {"id": "chapter-uuid", "name": "Học kì I", "order": 1},
        "lesson": {"id": "lesson-uuid", "name": "Phép cộng trong phạm vi 6", "order": 16}
      },
      "full_path": "Toán > SGK Toán Lớp 1 > Học kì I > Phép cộng trong phạm vi 6 > Phép cộng đơn giản"
    }
  ],
  "filters_applied": {
    "user_id": "student-uuid",
    "from_date": "2025-05-01",
    "to_date": "2025-05-31",
    "difficulty": "dễ",
    "is_correct": "false",
    "limit": 20
  },
  "total_records": 15,
  "success": true
}
```

### `GET /api/v1/students/learning-path/{user_id}`
Get detailed learning progression path for a student with timeline.

**Response:**
```json
{
  "user_id": "student-uuid",
  "learning_path": [
    {
      "study_date": "2025-05-27",
      "study_time": "10:00:00",
      "subject": {"id": "subject-uuid", "name": "Toán"},
      "typebook": {"id": "typebook-uuid", "name": "SGK Toán Lớp 1"},
      "chapter": {"id": "chapter-uuid", "name": "Học kì I", "order": 1},
      "lesson": {"id": "lesson-uuid", "name": "Các số 1, 2, 3", "order": 3},
      "question": {
        "id": "question-uuid",
        "title": "Đếm số táo",
        "page": 15,
        "difficulty": "dễ"
      },
      "answer": {
        "id": "answer-uuid",
        "is_correct": true,
        "duration_seconds": 120,
        "completion_time": "2025-05-27T10:02:00.000000"
      }
    }
  ],
  "study_sessions": {
    "2025-05-27": [
      {
        "study_time": "10:00:00",
        "subject": {"name": "Toán"},
        "lesson": {"name": "Các số 1, 2, 3"},
        "questions_answered": 5,
        "accuracy": 80.0
      }
    ],
    "2025-05-26": [...]
  },
  "progression_summary": {
    "subjects_completed": 2,
    "typebooks_completed": 3,
    "chapters_completed": 8,
    "lessons_completed": 25,
    "questions_answered": 150,
    "study_days": 15,
    "first_study_date": "2025-05-10",
    "latest_study_date": "2025-05-27"
  },
  "total_steps": 150,
  "success": true
}
```

---

## 🌐 Tree Structure Advanced

### `GET /api/v1/tree/ids-only`
Get minimal tree structure with only IDs for efficient loading.

**Response:**
```json
{
  "hierarchy_ids": {
    "subject-uuid": {
      "typebook-uuid": {
        "chapter-uuid": {
          "lesson-uuid": ["question1-uuid", "question2-uuid", "question3-uuid"]
        }
      }
    }
  },
  "user_ids": ["user1-uuid", "user2-uuid", "user3-uuid"],
  "success": true
}
```

### `GET /api/v1/tree/flat`
Get flattened tree structure for easy navigation and search.

**Response:**
```json
{
  "items": [
    {
      "id": "lesson-uuid",
      "name": "Các số 1, 2, 3",
      "type": "lesson",
      "path": "Toán > SGK Toán Lớp 1 > Học kì I > Các số 1, 2, 3",
      "parent_ids": {
        "subject_id": "subject-uuid",
        "typebook_id": "typebook-uuid",
        "chapter_id": "chapter-uuid"
      }
    },
    {
      "id": "question-uuid",
      "name": "Đếm số táo trong hình",
      "type": "question",
      "page": 15,
      "path": "Toán > SGK Toán Lớp 1 > Học kì I > Các số 1, 2, 3 > Đếm số táo trong hình",
      "parent_ids": {
        "subject_id": "subject-uuid",
        "typebook_id": "typebook-uuid",
        "chapter_id": "chapter-uuid",
        "lesson_id": "lesson-uuid"
      }
    }
  ],
  "users": [
    {
      "id": "user-uuid",
      "name": "Nguyễn Văn A",
      "email": "student@example.com",
      "type": "user"
    }
  ],
  "summary": {
    "total_lessons": 50,
    "total_questions": 500,
    "total_users": 150
  },
  "success": true
}
```

---

## 🔐 Security & Best Practices

### Authentication
Currently, the API does not implement authentication. For production use, consider implementing:
- JWT tokens for API authentication
- Role-based access control (RBAC)
- Rate limiting for API endpoints
- Input validation and sanitization

### Data Validation
- All inputs are validated for required fields
- Email format validation for user creation
- Progress values clamped between 0-100
- Batch size limits for bulk operations

### Error Handling Best Practices
```python
# Example error response structure
{
  "error": "Descriptive error message",
  "success": false,
  "details": {
    "field": "specific_field_name",
    "code": "VALIDATION_ERROR",
    "timestamp": "2025-05-27T10:00:00.000000"
  }
}
```

---

## 🚀 Deployment Guide

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
```

### Docker Compose with Neo4j
```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.0
    environment:
      NEO4J_AUTH: neo4j/your-password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  education-api:
    build: .
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USERNAME: neo4j
      NEO4J_PASSWORD: your-password
    ports:
      - "5000:5000"
    depends_on:
      - neo4j

volumes:
  neo4j_data:
```

### Production Considerations
- Use environment variables for sensitive configuration
- Set up proper logging and monitoring
- Configure CORS appropriately for your frontend domains
- Implement database connection pooling
- Set up health check endpoints for load balancers
- Configure proper Neo4j indexes for performance

---

## 📚 Additional Resources

### Neo4j Cypher Examples
```cypher
-- Find students who mastered specific knowledge
MATCH (u:User)-[r:LEARNED {status: 'mastered'}]->(k:Knowledge {subject: 'Toán'})
RETURN u.name, k.name, r.progress

-- Get learning progression timeline
MATCH (u:User {id: 'user-uuid'})-[:ANSWERED]->(a:Answer)-[:ANSWERS_QUESTION]->(q:Question)
RETURN date(a.completion_time) as study_date, count(a) as questions_answered, 
       avg(CASE WHEN a.is_correct THEN 1.0 ELSE 0.0 END) as accuracy
ORDER BY study_date

-- Find knowledge gaps (questions answered incorrectly multiple times)
MATCH (u:User {id: 'user-uuid'})-[:ANSWERED]->(a:Answer {is_correct: false})-[:ANSWERS_QUESTION]->(q:Question)
WITH q, count(a) as wrong_count
WHERE wrong_count >= 2
RETURN q.title, q.difficulty, wrong_count
ORDER BY wrong_count DESC
```

### Common Use Cases

1. **Adaptive Learning**: Use random question APIs with difficulty progression
2. **Progress Tracking**: Monitor student advancement through knowledge nodes
3. **Performance Analytics**: Identify learning gaps and strong areas
4. **Curriculum Management**: Organize content hierarchically
5. **Assessment Generation**: Create balanced quizzes across topics

### Integration Examples

#### Frontend Integration (JavaScript)
```javascript
// Get random quiz for student
const response = await fetch('/api/v1/questions/random/quiz?total_questions=10&user_id=student-uuid&exclude_answered=true');
const quiz = await response.json();

// Submit answer
await fetch('/api/v1/answers/bulk', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    answers: [{
      user_id: 'student-uuid',
      question_id: 'question-uuid',
      student_answer: 'Student response',
      is_correct: true,
      duration_seconds: 120
    }]
  })
});

// Update knowledge progress
await fetch(`/api/v1/users/${userId}/knowledge/${knowledgeId}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    progress: 85,
    status: 'completed'
  })
});
```

---

## 📞 Support & Contact

For technical support or questions about this API:
- Review the error messages and status codes
- Check the Neo4j database connectivity
- Verify environment variables are set correctly
- Ensure all required fields are provided in requests

**API Health Check**: `GET /api/v1/health`  
**Full Documentation**: `GET /` (this document)

---

*Last Updated: May 27, 2025*  
*API Version: v1*  
*Documentation Version: 1.0*