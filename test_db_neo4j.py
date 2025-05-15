import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

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
# Được chia thành các khối logic
CYPHER_QUERIES = [
    # --- 0. Dọn dẹp dữ liệu cũ (TÙY CHỌN - bỏ comment nếu muốn xóa sạch DB trước) ---
    # """
    # MATCH (n) DETACH DELETE n;
    # """,

    # --- 1. Tạo Môn học ---
    """
    CREATE (toan1:Subject {name: "Toán Lớp 1", grade: 1, description: "Môn Toán dành cho học sinh lớp 1."});
    """,

    # --- 2. Tạo Học sinh ---
    """
    CREATE (an:Student {studentId: "HS001", name: "Nguyễn Văn An", dob: date("2018-05-10")});
    CREATE (binh:Student {studentId: "HS002", name: "Trần Thị Bình", dob: date("2018-07-22")});
    CREATE (cuong:Student {studentId: "HS003", name: "Lê Minh Cường", dob: date("2018-03-15")});
    """,

    # --- 3. Tạo mối quan hệ Học sinh ĐĂNG KÝ Môn học ---
    """
    MATCH (s:Subject {name: "Toán Lớp 1"})
    MATCH (hs_an:Student {studentId: "HS001"})
    MATCH (hs_binh:Student {studentId: "HS002"})
    MATCH (hs_cuong:Student {studentId: "HS003"})
    CREATE (hs_an)-[:ENROLLED_IN {enrollmentDate: date()}]->(s);
    CREATE (hs_binh)-[:ENROLLED_IN {enrollmentDate: date()}]->(s);
    CREATE (hs_cuong)-[:ENROLLED_IN {enrollmentDate: date()}]->(s);
    """,

    # --- 4. Tạo các Câu hỏi cho Môn học ---
    """
    MATCH (s:Subject {name: "Toán Lớp 1"})
    CREATE (q1:Question {questionId: "Q001", text: "1 + 1 = ?", difficulty: "Dễ", topic: "Phép cộng"})-[:BELONGS_TO]->(s);
    CREATE (q2:Question {questionId: "Q002", text: "Hình vuông có mấy cạnh?", difficulty: "Trung bình", topic: "Hình học"})-[:BELONGS_TO]->(s);
    CREATE (q3:Question {questionId: "Q003", text: "Số liền sau của số 5 là số mấy?", difficulty: "Dễ", topic: "Dãy số"})-[:BELONGS_TO]->(s);
    """,

    # --- 5. Tạo các Câu trả lời cho từng Câu hỏi ---
    """
    // Câu trả lời cho Câu hỏi Q001
    MATCH (cauhoi1:Question {questionId: "Q001"})
    CREATE (ans1_1:Answer {answerId: "A001_1", text: "2", isCorrect: true});
    CREATE (ans1_2:Answer {answerId: "A001_2", text: "1", isCorrect: false});
    CREATE (ans1_3:Answer {answerId: "A001_3", text: "3", isCorrect: false});
    CREATE (cauhoi1)-[:HAS_OPTION]->(ans1_1);
    CREATE (cauhoi1)-[:HAS_OPTION]->(ans1_2);
    CREATE (cauhoi1)-[:HAS_OPTION]->(ans1_3);
    CREATE (cauhoi1)-[:CORRECT_ANSWER_IS]->(ans1_1);

    // Câu trả lời cho Câu hỏi Q002
    MATCH (cauhoi2:Question {questionId: "Q002"})
    CREATE (ans2_1:Answer {answerId: "A002_1", text: "4 cạnh", isCorrect: true});
    CREATE (ans2_2:Answer {answerId: "A002_2", text: "3 cạnh", isCorrect: false});
    CREATE (ans2_3:Answer {answerId: "A002_3", text: "5 cạnh", isCorrect: false});
    CREATE (cauhoi2)-[:HAS_OPTION]->(ans2_1);
    CREATE (cauhoi2)-[:HAS_OPTION]->(ans2_2);
    CREATE (cauhoi2)-[:HAS_OPTION]->(ans2_3);
    CREATE (cauhoi2)-[:CORRECT_ANSWER_IS]->(ans2_1);

    // Câu trả lời cho Câu hỏi Q003
    MATCH (cauhoi3:Question {questionId: "Q003"})
    CREATE (ans3_1:Answer {answerId: "A003_1", text: "Số 4", isCorrect: false});
    CREATE (ans3_2:Answer {answerId: "A003_2", text: "Số 6", isCorrect: true});
    CREATE (ans3_3:Answer {answerId: "A003_3", text: "Số 5", isCorrect: false});
    CREATE (cauhoi3)-[:HAS_OPTION]->(ans3_1);
    CREATE (cauhoi3)-[:HAS_OPTION]->(ans3_2);
    CREATE (cauhoi3)-[:HAS_OPTION]->(ans3_3);
    CREATE (cauhoi3)-[:CORRECT_ANSWER_IS]->(ans3_2);
    """,

    # --- 6. Tạo mối quan hệ Học sinh LÀM Câu hỏi và CHỌN Câu trả lời ---
    """
    MATCH (hs_an:Student {studentId: "HS001"})
    MATCH (hs_binh:Student {studentId: "HS002"})
    MATCH (q1:Question {questionId: "Q001"})
    MATCH (q2:Question {questionId: "Q002"})
    MATCH (ans_q1_an:Answer {answerId: "A001_1"})
    MATCH (ans_q1_binh:Answer {answerId: "A001_3"})
    MATCH (ans_q2_an:Answer {answerId: "A002_1"})

    // An làm câu Q001
    CREATE (hs_an)-[attempt1_an:ATTEMPTED_QUESTION {timestamp: datetime(), score: 10}]->(q1);
    CREATE (attempt1_an)-[:SELECTED_ANSWER]->(ans_q1_an);

    // Bình làm câu Q001
    CREATE (hs_binh)-[attempt1_binh:ATTEMPTED_QUESTION {timestamp: datetime(), score: 0}]->(q1);
    CREATE (attempt1_binh)-[:SELECTED_ANSWER]->(ans_q1_binh);

    // An làm câu Q002
    CREATE (hs_an)-[attempt2_an:ATTEMPTED_QUESTION {timestamp: datetime(), score: 10}]->(q2);
    CREATE (attempt2_an)-[:SELECTED_ANSWER]->(ans_q2_an);
    """,
    # --- Hoàn tất ---
    """
    RETURN "Tạo dữ liệu mẫu thành công!" AS message;
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
            self.driver = None # Đảm bảo driver là None nếu kết nối thất bại

    def close(self):
        if self.driver:
            self.driver.close()
            logging.info("Đã đóng kết nối Neo4j.")

    def create_data(self, queries):
        if not self.driver:
            logging.error("Không có kết nối driver. Không thể tạo dữ liệu.")
            return

        try:
            with self.driver.session() as session:
                for i, query_block in enumerate(queries):
                    if query_block.strip() and not query_block.strip().startswith("//"): # Bỏ qua dòng trống hoặc chỉ có comment
                        logging.info(f"--- Bắt đầu thực thi khối {i+1} ---")
                        
                        # Nếu khối truy vấn bắt đầu bằng RETURN, xử lý đặc biệt
                        if query_block.strip().startswith("RETURN"):
                            try:
                                final_message = session.run(query_block).single()
                                if final_message and final_message[0]:
                                    logging.info(f"Thông điệp cuối cùng từ DB: {final_message[0]}")
                            except Exception as e:
                                logging.error(f"Lỗi khi thực thi câu lệnh RETURN: {e}")
                        else:
                            # Tách các câu lệnh riêng biệt (chia theo dấu chấm phẩy)
                            individual_statements = [stmt.strip() for stmt in query_block.split(';') if stmt.strip()]
                            
                            for statement in individual_statements:
                                # Thêm dấu chấm phẩy vào cuối nếu không phải là comment
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
                                        # Không dừng toàn bộ quá trình nếu một câu lệnh lỗi
                        
                        logging.info(f"--- Hoàn thành khối {i+1} ---")
                logging.info("Tất cả các khối lệnh Cypher đã được thực thi.")
        except Exception as e:
            logging.error(f"Lỗi trong quá trình tạo dữ liệu: {e}")

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
        # creator.clear_database()

        # Tạo dữ liệu mẫu
        creator.create_data(CYPHER_QUERIES)

        # Đóng kết nối
        creator.close()
    else:
        logging.info("Không thể thực hiện các thao tác do lỗi kết nối ban đầu.")