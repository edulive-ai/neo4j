import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Tải biến môi trường từ file .env
load_dotenv()

# Lấy thông tin kết nối từ biến môi trường
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Kiểm tra các biến môi trường
if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    logging.error("Lỗi: Một hoặc nhiều biến môi trường NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD chưa được thiết lập.")
    logging.error("Vui lòng kiểm tra file .env của bạn hoặc thiết lập chúng trong môi trường hệ thống.")
    exit()

# Các câu lệnh Cypher để tạo dữ liệu
CYPHER_QUERIES = [
    # --- 0. Dọn dẹp dữ liệu cũ (TÙY CHỌN - bỏ comment nếu muốn xóa sạch DB trước) ---
    """
    MATCH (n) DETACH DELETE n;
    """,
    # --- 1. Tạo Môn học ---
    """
    
    CREATE (toan1:Subject {
        name: "Toán Lớp 1",
        grade: 1,
        description: "Môn Toán dành cho học sinh lớp 1 theo chương trình mới"
    });
    """,

    # --- 2. Tạo Học sinh ---
    """
    CREATE (hs1:Student {studentId: "HS001", name: "Nguyễn Văn An", dob: date("2018-05-10")});
    CREATE (hs2:Student {studentId: "HS002", name: "Trần Thị Bình", dob: date("2018-07-22")});
    CREATE (hs3:Student {studentId: "HS003", name: "Lê Minh Cường", dob: date("2018-03-15")});
    CREATE (hs4:Student {studentId: "HS004", name: "Phạm Thị Dung", dob: date("2018-09-30")});
    CREATE (hs5:Student {studentId: "HS005", name: "Hoàng Văn Em", dob: date("2018-11-05")});
    CREATE (hs6:Student {studentId: "HS006", name: "Đỗ Thị Gấm", dob: date("2018-04-18")});
    CREATE (hs7:Student {studentId: "HS007", name: "Vũ Minh Hùng", dob: date("2018-06-25")});
    CREATE (hs8:Student {studentId: "HS008", name: "Lý Thị Hương", dob: date("2018-08-12")});
    CREATE (hs9:Student {studentId: "HS009", name: "Trịnh Văn Khoa", dob: date("2018-10-20")});
    CREATE (hs10:Student {studentId: "HS010", name: "Bùi Thị Lan", dob: date("2018-12-15")});
    """,

    # --- 3. Tạo các Chương học ---
    """
    MATCH (s:Subject {name: "Toán Lớp 1"})
    CREATE (c1:Chapter {chapterId: "C1", name: "Số và phép tính", order: 1})-[:BELONGS_TO]->(s);
    CREATE (c2:Chapter {chapterId: "C2", name: "Hình học", order: 2})-[:BELONGS_TO]->(s);
    CREATE (c3:Chapter {chapterId: "C3", name: "Đo lường", order: 3})-[:BELONGS_TO]->(s);
    """,

    # --- 4. Tạo các Bài học trong Chương 1: Số và phép tính ---
    """
    MATCH (c:Chapter {chapterId: "C1"})
    CREATE (b1:Lesson {lessonId: "L1.1", name: "Các số từ 0 đến 10", order: 1})-[:BELONGS_TO]->(c);
    CREATE (b2:Lesson {lessonId: "L1.2", name: "Phép cộng trong phạm vi 10", order: 2})-[:BELONGS_TO]->(c);
    CREATE (b3:Lesson {lessonId: "L1.3", name: "Phép trừ trong phạm vi 10", order: 3})-[:BELONGS_TO]->(c);
    """,

    # --- 5. Tạo các Bài học trong Chương 2: Hình học ---
    """
    MATCH (c:Chapter {chapterId: "C2"})
    CREATE (b4:Lesson {lessonId: "L2.1", name: "Điểm và đoạn thẳng", order: 1})-[:BELONGS_TO]->(c);
    CREATE (b5:Lesson {lessonId: "L2.2", name: "Hình vuông, hình tròn", order: 2})-[:BELONGS_TO]->(c);
    CREATE (b6:Lesson {lessonId: "L2.3", name: "Hình tam giác, hình chữ nhật", order: 3})-[:BELONGS_TO]->(c);
    """,

    # --- 6. Tạo các Bài học trong Chương 3: Đo lường ---
    """
    MATCH (c:Chapter {chapterId: "C3"})
    CREATE (b7:Lesson {lessonId: "L3.1", name: "Đo độ dài", order: 1})-[:BELONGS_TO]->(c);
    CREATE (b8:Lesson {lessonId: "L3.2", name: "Đo thời gian", order: 2})-[:BELONGS_TO]->(c);
    """,

    # --- 7. Tạo các Câu hỏi cho Bài 1: Các số từ 0 đến 10 ---
    """
    MATCH (b:Lesson {lessonId: "L1.1"})
    CREATE (q1:Question {
        questionId: "Q1.1.1",
        text: "Số liền sau của số 5 là số mấy?",
        type: "multiple_choice",
        difficulty: "easy"
    })-[:BELONGS_TO]->(b);
    
    CREATE (q2:Question {
        questionId: "Q1.1.2",
        text: "Điền số thích hợp vào chỗ trống: 3 < ... < 5",
        type: "fill_blank",
        difficulty: "easy"
    })-[:BELONGS_TO]->(b);
    
    CREATE (q3:Question {
        questionId: "Q1.1.3",
        text: "Số 7 lớn hơn số 5. Đúng hay sai?",
        type: "true_false",
        difficulty: "easy"
    })-[:BELONGS_TO]->(b);
    """,

    # --- 8. Tạo đáp án cho các câu hỏi ---
    """
    // Đáp án cho Q1.1.1
    MATCH (q:Question {questionId: "Q1.1.1"})
    CREATE (a1:Answer {answerId: "A1.1.1.1", text: "6", isCorrect: true});
    CREATE (a2:Answer {answerId: "A1.1.1.2", text: "4", isCorrect: false});
    CREATE (a3:Answer {answerId: "A1.1.1.3", text: "7", isCorrect: false});
    CREATE (q)-[:HAS_OPTION]->(a1);
    CREATE (q)-[:HAS_OPTION]->(a2);
    CREATE (q)-[:HAS_OPTION]->(a3);
    CREATE (q)-[:CORRECT_ANSWER_IS]->(a1);

    // Đáp án cho Q1.1.2
    MATCH (q:Question {questionId: "Q1.1.2"})
    CREATE (a4:Answer {answerId: "A1.1.2.1", text: "4", isCorrect: true});
    CREATE (q)-[:CORRECT_ANSWER_IS]->(a4);

    // Đáp án cho Q1.1.3
    MATCH (q:Question {questionId: "Q1.1.3"})
    CREATE (a5:Answer {answerId: "A1.1.3.1", text: "Đúng", isCorrect: true});
    CREATE (a6:Answer {answerId: "A1.1.3.2", text: "Sai", isCorrect: false});
    CREATE (q)-[:HAS_OPTION]->(a5);
    CREATE (q)-[:HAS_OPTION]->(a6);
    CREATE (q)-[:CORRECT_ANSWER_IS]->(a5);
    """,

    # --- 9. Tạo kết quả làm bài của học sinh ---
    """
    MATCH (hs:Student {studentId: "HS001"})
    MATCH (q:Question {questionId: "Q1.1.1"})
    MATCH (a:Answer {answerId: "A1.1.1.1"})
    CREATE (hs)-[attempt:ATTEMPTED_QUESTION {
        timestamp: datetime(),
        score: 10,
        feedback: "Làm đúng"
    }]->(q);
    CREATE (attempt)-[:SELECTED_ANSWER]->(a);
    """,

    # --- 10. Tạo mối quan hệ Học sinh ĐĂNG KÝ Môn học ---
    """
    MATCH (s:Subject {name: "Toán Lớp 1"})
    MATCH (hs:Student)
    CREATE (hs)-[:ENROLLED_IN {enrollmentDate: date()}]->(s);
    """
]

class Neo4jDataCreator:
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            logging.info(f"Đã kết nối thành công tới Neo4j tại: {self.uri}")
        except Exception as e:
            logging.error(f"Lỗi kết nối Neo4j: {e}")
            self.driver = None

    def create_student_learning_data(self):
        """Tạo dữ liệu học tập cho học sinh"""
        if not self.driver:
            logging.error("Không có kết nối driver. Không thể tạo dữ liệu.")
            return

        try:
            with self.driver.session() as session:
                # Lấy danh sách học sinh
                students = session.run("MATCH (s:Student) RETURN s.studentId as id").data()
                
                # Lấy danh sách bài học
                lessons = session.run("MATCH (l:Lesson) RETURN l.lessonId as id").data()
                
                # Lấy danh sách câu hỏi
                questions = session.run("MATCH (q:Question) RETURN q.questionId as id").data()

                # Tạo dữ liệu học tập cho mỗi học sinh
                for student in students:
                    student_id = student['id']
                    
                    # Tạo tiến độ học tập cho mỗi bài học
                    for lesson in lessons:
                        lesson_id = lesson['id']
                        
                        # Tạo ngẫu nhiên thời gian học
                        study_time = datetime.now() - timedelta(days=random.randint(1, 30))
                        
                        # Tạo mối quan hệ học sinh đã học bài
                        session.run("""
                            MATCH (s:Student {studentId: $student_id})
                            MATCH (l:Lesson {lessonId: $lesson_id})
                            MERGE (s)-[r:STUDIED]->(l)
                            SET r.studyTime = $study_time,
                                r.completionStatus = $status,
                                r.score = $score
                        """, {
                            'student_id': student_id,
                            'lesson_id': lesson_id,
                            'study_time': study_time,
                            'status': random.choice(['completed', 'in_progress']),
                            'score': random.randint(0, 100)
                        })

                        # Tạo kết quả làm bài cho mỗi câu hỏi
                        for question in questions:
                            question_id = question['id']
                            
                            # Lấy đáp án đúng của câu hỏi
                            correct_answer = session.run("""
                                MATCH (q:Question {questionId: $question_id})-[:CORRECT_ANSWER_IS]->(a:Answer)
                                RETURN a.answerId as answer_id
                            """, {'question_id': question_id}).single()
                            
                            if correct_answer:
                                # Tạo ngẫu nhiên kết quả làm bài
                                is_correct = random.choice([True, False])
                                attempt_time = study_time + timedelta(minutes=random.randint(1, 60))
                                
                                # Tạo mối quan hệ học sinh làm câu hỏi
                                session.run("""
                                    MATCH (s:Student {studentId: $student_id})
                                    MATCH (q:Question {questionId: $question_id})
                                    MATCH (a:Answer {answerId: $answer_id})
                                    MERGE (s)-[r:ATTEMPTED_QUESTION]->(q)
                                    SET r.timestamp = $attempt_time,
                                        r.score = $score,
                                        r.feedback = $feedback
                                    MERGE (r)-[:SELECTED_ANSWER]->(a)
                                """, {
                                    'student_id': student_id,
                                    'question_id': question_id,
                                    'answer_id': correct_answer['answer_id'] if is_correct else random.choice([a['answer_id'] for a in session.run("MATCH (a:Answer) RETURN a.answerId as answer_id").data()]),
                                    'attempt_time': attempt_time,
                                    'score': 10 if is_correct else 0,
                                    'feedback': "Làm đúng" if is_correct else "Cần cố gắng thêm"
                                })

                logging.info("Đã tạo xong dữ liệu học tập cho học sinh")
        except Exception as e:
            logging.error(f"Lỗi khi tạo dữ liệu học tập: {e}")

    def create_data(self, queries):
        if not self.driver:
            logging.error("Không có kết nối driver. Không thể tạo dữ liệu.")
            return

        try:
            with self.driver.session() as session:
                for i, query_block in enumerate(queries):
                    if query_block.strip() and not query_block.strip().startswith("//"):
                        logging.info(f"--- Bắt đầu thực thi khối {i+1} ---")
                        
                        if query_block.strip().startswith("RETURN"):
                            try:
                                final_message = session.run(query_block).single()
                                if final_message and final_message[0]:
                                    logging.info(f"Thông điệp cuối cùng từ DB: {final_message[0]}")
                            except Exception as e:
                                logging.error(f"Lỗi khi thực thi câu lệnh RETURN: {e}")
                        else:
                            individual_statements = [stmt.strip() for stmt in query_block.split(';') if stmt.strip()]
                            
                            for statement in individual_statements:
                                if not statement.strip().startswith("//"):
                                    statement = statement + ";"
                                    try:
                                        logging.info(f"Đang thực thi câu lệnh Cypher: {statement[:100]}...")
                                        result = session.run(statement)
                                        summary = result.consume()
                                        logging.info(f"Counters: Nodes created={summary.counters.nodes_created}, Relationships created={summary.counters.relationships_created}")
                                    except Exception as e:
                                        logging.error(f"Lỗi khi thực thi câu lệnh: {e}")
                                        logging.error(f"Câu lệnh gây lỗi: {statement}")
                        
                        logging.info(f"--- Hoàn thành khối {i+1} ---")
                
                # Sau khi tạo dữ liệu cơ bản, tạo dữ liệu học tập cho học sinh
                self.create_student_learning_data()
                
                logging.info("Tất cả các khối lệnh Cypher đã được thực thi.")
        except Exception as e:
            logging.error(f"Lỗi trong quá trình tạo dữ liệu: {e}")

    def close(self):
        if self.driver:
            self.driver.close()
            logging.info("Đã đóng kết nối Neo4j.")

    def clear_database(self):
        """Tùy chọn: Xóa tất cả dữ liệu trong database."""
        if not self.driver:
            logging.error("Không có kết nối driver. Không thể xóa dữ liệu.")
            return
        logging.warning("!!! BẠN SẮP XÓA TOÀN BỘ DỮ LIỆU TRONG DATABASE !!!")
        confirmation = input("Bạn có chắc chắn muốn xóa toàn bộ dữ liệu? (yes/no): ")
        if confirmation.lower() == 'yes':
            try:
                with self.driver.session() as session:
                    logging.info("Đang xóa dữ liệu...")
                    session.execute_write(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))
                    logging.info("Đã xóa toàn bộ dữ liệu thành công.")
            except Exception as e:
                logging.error(f"Lỗi khi xóa dữ liệu: {e}")
        else:
            logging.info("Hủy bỏ thao tác xóa dữ liệu.")


if __name__ == "__main__":
    creator = Neo4jDataCreator(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

    if creator.driver:
        # TÙY CHỌN: Xóa database trước nếu bạn muốn (bỏ comment dòng dưới)
        creator.clear_database()

        # Tạo dữ liệu mẫu
        # creator.create_data(CYPHER_QUERIES)

        # Đóng kết nối
        creator.close()
    else:
        logging.info("Không thể thực hiện các thao tác do lỗi kết nối ban đầu.")