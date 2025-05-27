#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Educational Data Importer for Cánh Diều Math Grade 1
Imports data from JSON file into Neo4j with structure:
Users → Grade → Subject → TypeBook → Chapter → Lesson → Question → Answer
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from neo4j import GraphDatabase
import random
import sys
from dotenv import load_dotenv

load_dotenv()

class Neo4jEducationImporter:
    def __init__(self, json_file_path="toan-lop1-canh-dieu.json"):
        """
        Initialize the importer
        
        Args:
            json_file_path (str): Path to the JSON data file
        """
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USERNAME") 
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None
        self.json_file_path = json_file_path
        self.math_data = []
        
        # Load dữ liệu từ file JSON
        self.load_json_data()
        
    def load_json_data(self):
        """Load dữ liệu từ file JSON"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.math_data = json.load(f)
            print(f"✅ Đã load {len(self.math_data)} câu hỏi từ file {self.json_file_path}")
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file {self.json_file_path}")
            print(f"📂 Vui lòng đảm bảo file {self.json_file_path} có trong thư mục hiện tại")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Lỗi đọc file JSON: {e}")
            raise
        except Exception as e:
            print(f"❌ Lỗi load dữ liệu: {e}")
            raise
        
    def connect(self):
        """Kết nối đến Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
            print("✅ Kết nối Neo4j thành công!")
        except Exception as e:
            print(f"❌ Lỗi kết nối Neo4j: {e}")
            print("🔧 Vui lòng kiểm tra:")
            print("  - Neo4j đang chạy")
            print("  - Thông tin kết nối đúng")
            print("  - Biến môi trường đã được thiết lập")
            raise

    def close(self):
        """Đóng kết nối"""
        if self.driver:
            self.driver.close()
            print("🔒 Đã đóng kết nối Neo4j")

    def clear_database(self):
        """Xóa toàn bộ dữ liệu trong database"""
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            print("🗑️ Đã xóa toàn bộ dữ liệu trong database")
        except Exception as e:
            print(f"❌ Lỗi xóa database: {e}")
            raise

    def create_constraints_and_indexes(self):
        """Tạo constraints và indexes"""
        constraints_queries = [
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT grade_id_unique IF NOT EXISTS FOR (g:Grade) REQUIRE g.id IS UNIQUE",
            "CREATE CONSTRAINT subject_id_unique IF NOT EXISTS FOR (s:Subject) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT type_book_id_unique IF NOT EXISTS FOR (tb:TypeBook) REQUIRE tb.id IS UNIQUE",
            "CREATE CONSTRAINT chapter_id_unique IF NOT EXISTS FOR (c:Chapter) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT lesson_id_unique IF NOT EXISTS FOR (l:Lesson) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT question_id_unique IF NOT EXISTS FOR (q:Question) REQUIRE q.id IS UNIQUE",
            "CREATE CONSTRAINT answer_id_unique IF NOT EXISTS FOR (a:Answer) REQUIRE a.id IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for query in constraints_queries:
                try:
                    session.run(query)
                except Exception as e:
                    # Constraint có thể đã tồn tại
                    pass
        
        print("📋 Đã tạo constraints và indexes")

    def generate_timestamp(self, days_ago=0, hours_ago=0, minutes_ago=0):
        """Tạo timestamp với offset"""
        base_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        return base_time.isoformat()

    def create_users(self):
        """Tạo dữ liệu Users - học sinh"""
        users_data = [
            {"id": str(uuid.uuid4()), "name": "Nguyễn Văn An", "email": "an.nguyen@student.com", "age": 7},
            {"id": str(uuid.uuid4()), "name": "Trần Thị Bình", "email": "binh.tran@student.com", "age": 6},
            {"id": str(uuid.uuid4()), "name": "Lê Văn Cường", "email": "cuong.le@student.com", "age": 7},
            {"id": str(uuid.uuid4()), "name": "Phạm Thị Dung", "email": "dung.pham@student.com", "age": 6},
            {"id": str(uuid.uuid4()), "name": "Hoàng Văn Em", "email": "em.hoang@student.com", "age": 7},
            {"id": str(uuid.uuid4()), "name": "Vũ Thị Hoa", "email": "hoa.vu@student.com", "age": 6},
            {"id": str(uuid.uuid4()), "name": "Đặng Văn Khoa", "email": "khoa.dang@student.com", "age": 7},
            {"id": str(uuid.uuid4()), "name": "Bùi Thị Lan", "email": "lan.bui@student.com", "age": 6}
        ]
        
        for user in users_data:
            user["createdAt"] = self.generate_timestamp(30)
            user["updatedAt"] = self.generate_timestamp(1)
        
        query = """
        CREATE (u:User {
            id: $id,
            name: $name,
            email: $email,
            age: $age,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        """
        
        with self.driver.session() as session:
            for user_data in users_data:
                session.run(query, user_data)
        
        print(f"👥 Đã tạo {len(users_data)} users")
        return [u["id"] for u in users_data]

    def create_grade(self):
        """Tạo dữ liệu Grade"""
        grade_data = {
            "id": str(uuid.uuid4()),
            "name": "Lớp 1",
            "level": 1,
            "description": "Lớp học cấp tiểu học lớp 1",
            "createdAt": self.generate_timestamp(60),
            "updatedAt": self.generate_timestamp(1)
        }
        
        query = """
        CREATE (g:Grade {
            id: $id,
            name: $name,
            level: $level,
            description: $description,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        """
        
        with self.driver.session() as session:
            session.run(query, grade_data)
        
        print(f"🎓 Đã tạo grade: {grade_data['name']}")
        return grade_data["id"]

    def create_subject(self, grade_id):
        """Tạo dữ liệu Subject"""
        subject_data = {
            "id": str(uuid.uuid4()),
            "name": "Toán học",
            "code": "TOAN1",
            "description": "Môn Toán học lớp 1",
            "createdAt": self.generate_timestamp(50),
            "updatedAt": self.generate_timestamp(1)
        }
        
        # Tạo subject
        query = """
        CREATE (s:Subject {
            id: $id,
            name: $name,
            code: $code,
            description: $description,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        """
        
        with self.driver.session() as session:
            session.run(query, subject_data)
        
        # Tạo relationship với Grade
        relationship_query = """
        MATCH (g:Grade {id: $grade_id})
        MATCH (s:Subject {id: $subject_id})
        CREATE (s)-[:BELONGS_TO_GRADE]->(g)
        """
        
        with self.driver.session() as session:
            session.run(relationship_query, {
                "grade_id": grade_id,
                "subject_id": subject_data["id"]
            })
        
        print(f"📚 Đã tạo subject: {subject_data['name']}")
        return subject_data["id"]

    def create_type_book(self, subject_id):
        """Tạo dữ liệu TypeBook"""
        type_book_data = {
            "id": str(uuid.uuid4()),
            "name": "Cánh Diều",
            "publisher": "Nhà xuất bản Giáo dục Việt Nam",
            "edition": "2021",
            "description": "Bộ sách giáo khoa Cánh Diều",
            "createdAt": self.generate_timestamp(45),
            "updatedAt": self.generate_timestamp(1)
        }
        
        # Tạo type book
        query = """
        CREATE (tb:TypeBook {
            id: $id,
            name: $name,
            publisher: $publisher,
            edition: $edition,
            description: $description,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        """
        
        with self.driver.session() as session:
            session.run(query, type_book_data)
        
        # Tạo relationship với Subject
        relationship_query = """
        MATCH (s:Subject {id: $subject_id})
        MATCH (tb:TypeBook {id: $type_book_id})
        CREATE (tb)-[:BELONGS_TO_SUBJECT]->(s)
        """
        
        with self.driver.session() as session:
            session.run(relationship_query, {
                "subject_id": subject_id,
                "type_book_id": type_book_data["id"]
            })
        
        print(f"📖 Đã tạo type book: {type_book_data['name']}")
        return type_book_data["id"]

    def create_chapters_and_lessons(self, type_book_id):
        """Tạo dữ liệu Chapters và Lessons từ JSON data"""
        # Lấy danh sách unique chapters và lessons
        chapters_dict = {}
        lessons_dict = {}
        
        for item in self.math_data:
            chapter_name = item["chaper"]  # Note: "chaper" từ JSON gốc
            lesson_name = item["lessons"]
            
            if chapter_name not in chapters_dict:
                chapters_dict[chapter_name] = {
                    "id": str(uuid.uuid4()),
                    "name": chapter_name,
                    "description": f"Chương học: {chapter_name}",
                    "order": len(chapters_dict) + 1,
                    "createdAt": self.generate_timestamp(40),
                    "updatedAt": self.generate_timestamp(1)
                }
            
            lesson_key = f"{chapter_name}||{lesson_name}"
            if lesson_key not in lessons_dict:
                lessons_dict[lesson_key] = {
                    "id": str(uuid.uuid4()),
                    "name": lesson_name,
                    "description": f"Bài học: {lesson_name}",
                    "order": len([k for k in lessons_dict.keys() if k.startswith(chapter_name)]) + 1,
                    "chapter_id": chapters_dict[chapter_name]["id"],
                    "chapter_name": chapter_name,
                    "createdAt": self.generate_timestamp(35),
                    "updatedAt": self.generate_timestamp(1)
                }
        
        # Tạo chapters
        chapter_query = """
        CREATE (c:Chapter {
            id: $id,
            name: $name,
            description: $description,
            order: $order,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        """
        
        with self.driver.session() as session:
            for chapter_data in chapters_dict.values():
                session.run(chapter_query, chapter_data)
        
        # Tạo relationship Chapter -> TypeBook
        chapter_relationship_query = """
        MATCH (tb:TypeBook {id: $type_book_id})
        MATCH (c:Chapter {id: $chapter_id})
        CREATE (c)-[:BELONGS_TO_TYPE_BOOK]->(tb)
        """
        
        with self.driver.session() as session:
            for chapter_data in chapters_dict.values():
                session.run(chapter_relationship_query, {
                    "type_book_id": type_book_id,
                    "chapter_id": chapter_data["id"]
                })
        
        # Tạo lessons
        lesson_query = """
        CREATE (l:Lesson {
            id: $id,
            name: $name,
            description: $description,
            order: $order,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        """
        
        with self.driver.session() as session:
            for lesson_data in lessons_dict.values():
                session.run(lesson_query, {
                    "id": lesson_data["id"],
                    "name": lesson_data["name"],
                    "description": lesson_data["description"],
                    "order": lesson_data["order"],
                    "createdAt": lesson_data["createdAt"],
                    "updatedAt": lesson_data["updatedAt"]
                })
        
        # Tạo relationship Lesson -> Chapter
        lesson_relationship_query = """
        MATCH (c:Chapter {id: $chapter_id})
        MATCH (l:Lesson {id: $lesson_id})
        CREATE (l)-[:BELONGS_TO_CHAPTER]->(c)
        """
        
        with self.driver.session() as session:
            for lesson_data in lessons_dict.values():
                session.run(lesson_relationship_query, {
                    "chapter_id": lesson_data["chapter_id"],
                    "lesson_id": lesson_data["id"]
                })
        
        print(f"📑 Đã tạo {len(chapters_dict)} chapters và {len(lessons_dict)} lessons")
        return chapters_dict, lessons_dict

    def create_questions(self, lessons_dict):
        """Tạo dữ liệu Questions từ JSON data"""
        questions_data = []
        
        for item in self.math_data:
            lesson_key = f"{item['chaper']}||{item['lessons']}"
            if lesson_key in lessons_dict:
                lesson_id = lessons_dict[lesson_key]["id"]
                
                question_data = {
                    "id": str(uuid.uuid4()),
                    "title": item["title"],
                    "content": item["questions"],
                    "correct_answer": item["answers"],
                    "difficulty": item["difficulty"],
                    "page": item["page"],
                    "image_question": item.get("image_question", ""),
                    "image_answer": item.get("image_answer", ""),
                    "lesson_id": lesson_id,
                    "createdAt": self.generate_timestamp(30),
                    "updatedAt": self.generate_timestamp(1)
                }
                questions_data.append(question_data)
        
        # Tạo questions
        query = """
        CREATE (q:Question {
            id: $id,
            title: $title,
            content: $content,
            correct_answer: $correct_answer,
            difficulty: $difficulty,
            page: $page,
            image_question: $image_question,
            image_answer: $image_answer,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        """
        
        with self.driver.session() as session:
            for question_data in questions_data:
                session.run(query, {
                    "id": question_data["id"],
                    "title": question_data["title"],
                    "content": question_data["content"],
                    "correct_answer": question_data["correct_answer"],
                    "difficulty": question_data["difficulty"],
                    "page": question_data["page"],
                    "image_question": question_data["image_question"],
                    "image_answer": question_data["image_answer"],
                    "createdAt": question_data["createdAt"],
                    "updatedAt": question_data["updatedAt"]
                })
        
        # Tạo relationship Question -> Lesson
        relationship_query = """
        MATCH (l:Lesson {id: $lesson_id})
        MATCH (q:Question {id: $question_id})
        CREATE (q)-[:BELONGS_TO_LESSON]->(l)
        """
        
        with self.driver.session() as session:
            for question_data in questions_data:
                session.run(relationship_query, {
                    "lesson_id": question_data["lesson_id"],
                    "question_id": question_data["id"]
                })
        
        print(f"❓ Đã tạo {len(questions_data)} questions")
        return [q["id"] for q in questions_data]

    def create_answers(self, user_ids, question_ids):
        """Tạo dữ liệu Answers - câu trả lời của học sinh"""
        answers_data = []
        
        print("✍️ Đang tạo câu trả lời cho từng học sinh...")
        
        # Mỗi user trả lời một số câu hỏi ngẫu nhiên
        for i, user_id in enumerate(user_ids):
            print(f"  👤 Tạo câu trả lời cho học sinh {i+1}/{len(user_ids)}")
            
            # Mỗi user trả lời 60-80% số câu hỏi
            num_questions_to_answer = random.randint(
                int(len(question_ids) * 0.6), 
                int(len(question_ids) * 0.8)
            )
            
            selected_questions = random.sample(question_ids, num_questions_to_answer)
            
            for question_id in selected_questions:
                # Thời gian bắt đầu làm bài (trong vòng 30 ngày qua)
                start_time = self.generate_timestamp(
                    days_ago=random.randint(1, 30),
                    hours_ago=random.randint(0, 23),
                    minutes_ago=random.randint(0, 59)
                )
                
                # Thời gian hoàn thành (từ 30 giây đến 10 phút sau khi bắt đầu)
                completion_time_minutes = random.randint(1, 10)
                completion_time_seconds = random.randint(0, 59)
                
                # Tính toán thời gian hoàn thành
                start_datetime = datetime.fromisoformat(start_time)
                completion_datetime = start_datetime + timedelta(
                    minutes=completion_time_minutes, 
                    seconds=completion_time_seconds
                )
                
                # Đánh giá đúng/sai (70% làm đúng, 30% làm sai)
                is_correct = random.choices([True, False], weights=[70, 30])[0]
                
                # Tạo câu trả lời của học sinh
                if is_correct:
                    student_answer = "Câu trả lời đúng của học sinh"
                else:
                    student_answer = "Câu trả lời sai của học sinh"
                
                answer_data = {
                    "id": str(uuid.uuid4()),
                    "student_answer": student_answer,
                    "is_correct": is_correct,
                    "start_time": start_time,
                    "completion_time": completion_datetime.isoformat(),
                    "duration_seconds": completion_time_minutes * 60 + completion_time_seconds,
                    "user_id": user_id,
                    "question_id": question_id,
                    "createdAt": completion_datetime.isoformat(),
                    "updatedAt": completion_datetime.isoformat()
                }
                answers_data.append(answer_data)
        
        print(f"  📝 Chuẩn bị insert {len(answers_data)} answers vào database...")
        
        # Tạo answers
        query = """
        CREATE (a:Answer {
            id: $id,
            student_answer: $student_answer,
            is_correct: $is_correct,
            start_time: $start_time,
            completion_time: $completion_time,
            duration_seconds: $duration_seconds,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        """
        
        with self.driver.session() as session:
            for answer_data in answers_data:
                session.run(query, {
                    "id": answer_data["id"],
                    "student_answer": answer_data["student_answer"],
                    "is_correct": answer_data["is_correct"],
                    "start_time": answer_data["start_time"],
                    "completion_time": answer_data["completion_time"],
                    "duration_seconds": answer_data["duration_seconds"],
                    "createdAt": answer_data["createdAt"],
                    "updatedAt": answer_data["updatedAt"]
                })
        
        print("  🔗 Đang tạo relationships...")
        
        # Tạo relationships
        user_relationship_query = """
        MATCH (u:User {id: $user_id})
        MATCH (a:Answer {id: $answer_id})
        CREATE (u)-[:ANSWERED]->(a)
        """
        
        question_relationship_query = """
        MATCH (q:Question {id: $question_id})
        MATCH (a:Answer {id: $answer_id})
        CREATE (a)-[:ANSWERS_QUESTION]->(q)
        """
        
        with self.driver.session() as session:
            for answer_data in answers_data:
                session.run(user_relationship_query, {
                    "user_id": answer_data["user_id"],
                    "answer_id": answer_data["id"]
                })
                
                session.run(question_relationship_query, {
                    "question_id": answer_data["question_id"],
                    "answer_id": answer_data["id"]
                })
        
        print(f"✅ Đã tạo {len(answers_data)} answers")
        return len(answers_data)

    def run_import(self):
        """Chạy toàn bộ quá trình import dữ liệu"""
        try:
            print("🚀 Bắt đầu import dữ liệu giáo dục vào Neo4j...")
            print(f"📂 Sử dụng file dữ liệu: {self.json_file_path}")
            
            # Kết nối và chuẩn bị database
            self.connect()
            self.clear_database()
            self.create_constraints_and_indexes()
            
            # Import dữ liệu theo cấu trúc phân cấp
            print("\n📊 Đang tạo cấu trúc dữ liệu...")
            user_ids = self.create_users()
            grade_id = self.create_grade()
            subject_id = self.create_subject(grade_id)
            type_book_id = self.create_type_book(subject_id)
            chapters_dict, lessons_dict = self.create_chapters_and_lessons(type_book_id)
            question_ids = self.create_questions(lessons_dict)
            total_answers = self.create_answers(user_ids, question_ids)
            
            print("\n✅ Import dữ liệu hoàn tất!")
            print("\n📈 Thống kê dữ liệu đã tạo:")
            self.print_statistics()
            
        except Exception as e:
            print(f"❌ Lỗi trong quá trình import: {e}")
            raise
        finally:
            self.close()

    def print_statistics(self):
        """In thống kê dữ liệu đã tạo"""
        queries = {
            "Users": "MATCH (u:User) RETURN count(u) as count",
            "Grades": "MATCH (g:Grade) RETURN count(g) as count", 
            "Subjects": "MATCH (s:Subject) RETURN count(s) as count",
            "Type Books": "MATCH (tb:TypeBook) RETURN count(tb) as count",
            "Chapters": "MATCH (c:Chapter) RETURN count(c) as count",
            "Lessons": "MATCH (l:Lesson) RETURN count(l) as count",
            "Questions": "MATCH (q:Question) RETURN count(q) as count",
            "Answers": "MATCH (a:Answer) RETURN count(a) as count"
        }
        
        with self.driver.session() as session:
            for entity, query in queries.items():
                result = session.run(query)
                count = result.single()["count"]
                print(f"  • {entity}: {count}")

    def verify_relationships(self):
        """Kiểm tra các mối quan hệ đã được tạo đúng"""
        relationship_queries = {
            "BELONGS_TO_GRADE": "MATCH ()-[r:BELONGS_TO_GRADE]->() RETURN count(r) as count",
            "BELONGS_TO_SUBJECT": "MATCH ()-[r:BELONGS_TO_SUBJECT]->() RETURN count(r) as count", 
            "BELONGS_TO_TYPE_BOOK": "MATCH ()-[r:BELONGS_TO_TYPE_BOOK]->() RETURN count(r) as count",
            "BELONGS_TO_CHAPTER": "MATCH ()-[r:BELONGS_TO_CHAPTER]->() RETURN count(r) as count",
            "BELONGS_TO_LESSON": "MATCH ()-[r:BELONGS_TO_LESSON]->() RETURN count(r) as count",
            "ANSWERED": "MATCH ()-[r:ANSWERED]->() RETURN count(r) as count",
            "ANSWERS_QUESTION": "MATCH ()-[r:ANSWERS_QUESTION]->() RETURN count(r) as count"
        }
        
        print("\n🔗 Thống kê mối quan hệ:")
        with self.driver.session() as session:
            for rel_type, query in relationship_queries.items():
                result = session.run(query)
                count = result.single()["count"]
                print(f"  • {rel_type}: {count}")

    def get_sample_queries(self):
        """Trả về các query mẫu để khám phá dữ liệu"""
        queries = {
            "Xem tất cả users": "MATCH (u:User) RETURN u",
            "Xem progress của từng học sinh": """
                MATCH (u:User)-[:ANSWERED]->(a:Answer)-[:ANSWERS_QUESTION]->(q:Question)
                RETURN u.name as student_name, 
                       count(q) as total_questions, 
                       count(CASE WHEN a.is_correct = true THEN 1 END) as correct_answers,
                       round(100.0 * count(CASE WHEN a.is_correct = true THEN 1 END) / count(q), 2) as accuracy_percentage
                ORDER BY accuracy_percentage DESC
            """,
            "Xem câu hỏi khó nhất": """
                MATCH (q:Question)<-[:ANSWERS_QUESTION]-(a:Answer)
                RETURN q.title, q.difficulty, q.page,
                       count(a) as total_attempts,
                       count(CASE WHEN a.is_correct = true THEN 1 END) as correct_attempts,
                       round(100.0 * count(CASE WHEN a.is_correct = true THEN 1 END) / count(a), 2) as success_rate
                ORDER BY success_rate ASC
                LIMIT 10
            """,
            "Xem thời gian làm bài trung bình": """
                MATCH (u:User)-[:ANSWERED]->(a:Answer)
                RETURN u.name as student_name, 
                       round(avg(a.duration_seconds), 0) as avg_duration_seconds,
                       round(avg(a.duration_seconds)/60.0, 1) as avg_duration_minutes
                ORDER BY avg_duration_seconds
            """,
            "Xem cấu trúc dữ liệu đầy đủ": """
                MATCH path = (u:User)-[:ANSWERED]->(a:Answer)-[:ANSWERS_QUESTION]->(q:Question)
                            -[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
                            -[:BELONGS_TO_TYPE_BOOK]->(tb:TypeBook)-[:BELONGS_TO_SUBJECT]->(s:Subject)
                            -[:BELONGS_TO_GRADE]->(g:Grade)
                RETURN u.name as student, c.name as chapter, l.name as lesson, 
                       q.title as question, a.is_correct as correct, a.duration_seconds as duration
                LIMIT 10
            """,
            "Thống kê theo chapter": """
                MATCH (c:Chapter)<-[:BELONGS_TO_LESSON]-(l:Lesson)<-[:BELONGS_TO_QUESTION]-(q:Question)
                      <-[:ANSWERS_QUESTION]-(a:Answer)
                RETURN c.name as chapter_name,
                       count(DISTINCT q) as total_questions,
                       count(a) as total_attempts,
                       count(CASE WHEN a.is_correct = true THEN 1 END) as correct_attempts,
                       round(100.0 * count(CASE WHEN a.is_correct = true THEN 1 END) / count(a), 2) as success_rate
                ORDER BY success_rate DESC
            """
        }
        return queries


def check_environment():
    """Kiểm tra môi trường và các yêu cầu"""
    print("🔍 Kiểm tra môi trường...")
    
    # Kiểm tra biến môi trường
    required_env_vars = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Thiếu các biến môi trường: {', '.join(missing_vars)}")
        print("\n📝 Vui lòng thiết lập các biến môi trường sau:")
        for var in missing_vars:
            if var == "NEO4J_URI":
                print(f"  export {var}='bolt://localhost:7687'")
            elif var == "NEO4J_USERNAME":
                print(f"  export {var}='neo4j'")
            else:
                print(f"  export {var}='your_password'")
        return False
    
    # Kiểm tra file JSON
    json_file = "toan-lop1-canh-dieu.json"
    if not os.path.exists(json_file):
        print(f"❌ Không tìm thấy file {json_file}")
        print(f"📂 Vui lòng đảm bảo file {json_file} có trong thư mục hiện tại:")
        print(f"   {os.getcwd()}")
        return False
    
    # Kiểm tra thư viện neo4j
    try:
        import neo4j
        print("✅ Thư viện neo4j đã được cài đặt")
    except ImportError:
        print("❌ Chưa cài đặt thư viện neo4j")
        print("📦 Vui lòng chạy: pip install neo4j")
        return False
    
    print("✅ Môi trường đã sẵn sàng!")
    return True


def main():
    """Hàm main để chạy script"""
    print("📚 Neo4j Educational Data Importer - Cánh Diều")
    print("=" * 60)
    print("📖 Import dữ liệu sách giáo khoa Toán lớp 1 vào Neo4j")
    print("🏗️  Cấu trúc: Users → Grade → Subject → TypeBook → Chapter → Lesson → Question → Answer")
    print("=" * 60)
    
    # Kiểm tra môi trường
    if not check_environment():
        return 1
    
    # Tạo và chạy importer
    try:
        json_file = "toan-lop1-canh-dieu.json"
        importer = Neo4jEducationImporter(json_file)
        
        # Chạy import
        importer.run_import()
        
        # Kiểm tra relationships
        print("\n🔍 Kiểm tra relationships...")
        importer.connect()
        importer.verify_relationships()
        importer.close()
        
        # Hiển thị thông tin hoàn thành
        print("\n🎉 Import dữ liệu thành công!")
        print("\n📊 Cấu trúc dữ liệu đã được tạo:")
        print("  👥 Users (học sinh)")
        print("  🎓 Grade (lớp học)")  
        print("  📚 Subject (môn học)")
        print("  📖 TypeBook (loại sách)")
        print("  📑 Chapters (chương)")
        print("  📝 Lessons (bài học)")
        print("  ❓ Questions (câu hỏi)")
        print("  ✍️  Answers (câu trả lời)")
        
        # Hiển thị các query mẫu
        print("\n💡 Các query mẫu để khám phá dữ liệu:")
        queries = importer.get_sample_queries()
        for description, query in queries.items():
            print(f"\n📋 {description}:")
            print(f"```cypher")
            print(query.strip())
            print("```")
        
        print("\n🎯 Bạn có thể sử dụng Neo4j Browser tại: http://localhost:7474")
        
    except KeyboardInterrupt:
        print("\n⚠️ Import bị hủy bởi người dùng")
        return 1
    except Exception as e:
        print(f"\n💥 Import thất bại: {e}")
        print(f"📍 Chi tiết lỗi: {type(e).__name__}")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n💥 Lỗi không mong muốn: {e}")
        sys.exit(1)