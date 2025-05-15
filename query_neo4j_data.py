import os
import logging
import json
from datetime import date, datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tabulate import tabulate
import sys

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Class để chuyển đổi các đối tượng neo4j thành JSON
class Neo4jEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super(Neo4jEncoder, self).default(obj)

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

# Các truy vấn dữ liệu Neo4j
QUERIES = {
    "all_subjects": {
        "query": "MATCH (s:Subject) RETURN s.name AS TênMônHọc, s.grade AS Lớp, s.description AS MôTả",
        "description": "Tất cả các môn học"
    },
    "all_students": {
        "query": "MATCH (s:Student) RETURN s.studentId AS MãHọcSinh, s.name AS HọTên, s.dob AS NgàySinh",
        "description": "Tất cả học sinh"
    },
    "student_enrollments": {
        "query": """
        MATCH (s:Student)-[e:ENROLLED_IN]->(sub:Subject)
        RETURN s.name AS HọcSinh, sub.name AS MônHọc, e.enrollmentDate AS NgàyĐăngKý
        """,
        "description": "Thông tin đăng ký môn học"
    },
    "all_questions": {
        "query": """
        MATCH (q:Question)-[:BELONGS_TO]->(s:Subject)
        RETURN q.questionId AS MãCâuHỏi, q.text AS NộiDungCâuHỏi, q.difficulty AS MứcĐộ, s.name AS MônHọc
        """,
        "description": "Tất cả câu hỏi"
    },
    "question_with_answers": {
        "query": """
        MATCH (q:Question)-[:HAS_OPTION]->(a:Answer)
        RETURN q.questionId AS MãCâuHỏi, q.text AS NộiDungCâuHỏi, 
               a.text AS ĐápÁn, a.isCorrect AS LàĐápÁnĐúng
        ORDER BY q.questionId, a.isCorrect DESC
        """,
        "description": "Câu hỏi và đáp án"
    },
    "correct_answers": {
        "query": """
        MATCH (q:Question)-[:CORRECT_ANSWER_IS]->(a:Answer)
        RETURN q.questionId AS MãCâuHỏi, q.text AS NộiDungCâuHỏi, 
               a.text AS ĐápÁnĐúng, a.answerId AS MãĐápÁn
        """,
        "description": "Câu hỏi và đáp án đúng"
    },
    "student_question_attempts": {
        "query": """
        MATCH p=(s:Student)-[att:ATTEMPTED_QUESTION]->(q:Question)
        RETURN s.name AS HọcSinh, q.text AS CâuHỏi, 
               q.questionId AS MãCâuHỏi, att.score AS ĐiểmSố, 
               att.timestamp AS ThờiGianLàm
        """,
        "description": "Thống kê bài làm của học sinh"
    },
    "student_answers": {
        "query": """
        MATCH (s:Student)-[att:ATTEMPTED_QUESTION]->(q:Question),
              (att)-[sel:SELECTED_ANSWER]->(a:Answer)
        RETURN s.name AS HọcSinh, q.text AS CâuHỏi,
               a.text AS ĐápÁnĐãChọn, att.score AS ĐiểmSố
        """,
        "description": "Đáp án đã chọn của học sinh"
    },
    "student_performance_by_subject": {
        "query": """
        MATCH (s:Student)-[att:ATTEMPTED_QUESTION]->(q:Question)-[:BELONGS_TO]->(sub:Subject)
        RETURN s.name AS HọcSinh, sub.name AS MônHọc, 
               COUNT(q) AS SốCâuĐãLàm, SUM(att.score) AS TổngĐiểm,
               AVG(att.score) AS ĐiểmTrungBình
        GROUP BY s.name, sub.name
        """,
        "description": "Thống kê kết quả học tập theo môn học"
    },
    "db_schema": {
        "query": """
        CALL db.schema.visualization()
        """,
        "description": "Cấu trúc sơ đồ cơ sở dữ liệu"
    },
    "relationship_types": {
        "query": """
        CALL db.relationshipTypes()
        """,
        "description": "Các loại mối quan hệ trong cơ sở dữ liệu"
    },
    "node_labels": {
        "query": """
        CALL db.labels()
        """,
        "description": "Các nhãn node trong cơ sở dữ liệu"
    }
}

class Neo4jDataRetriever:
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

    def close(self):
        if self.driver:
            self.driver.close()
            logging.info("Đã đóng kết nối Neo4j.")

    def execute_query(self, query_name, output_format="table"):
        """
        Thực thi truy vấn theo tên và hiển thị kết quả.
        
        Args:
            query_name (str): Tên của truy vấn để thực thi
            output_format (str): Định dạng đầu ra - "table" hoặc "json"
        """
        if not self.driver:
            logging.error("Không có kết nối Neo4j. Không thể thực thi truy vấn.")
            return

        if query_name not in QUERIES:
            logging.error(f"Không tìm thấy truy vấn với tên: {query_name}")
            self.list_available_queries()
            return

        query_info = QUERIES[query_name]
        query = query_info["query"]
        description = query_info["description"]
        
        if output_format == "table":
            print(f"\n=== {description.upper()} ===\n")
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                records = list(result)
                
                if not records:
                    if output_format == "table":
                        print("Không có dữ liệu nào được tìm thấy.")
                    return []
                
                # Lấy tên các cột
                columns = result.keys()
                
                if output_format == "json":
                    # Chuyển đổi kết quả thành danh sách các dictionary
                    json_data = []
                    for record in records:
                        record_dict = {}
                        for col in columns:
                            record_dict[col] = record[col]
                        json_data.append(record_dict)
                    
                    # Xuất dữ liệu JSON
                    print(json.dumps(json_data, ensure_ascii=False, indent=2, cls=Neo4jEncoder))
                    return json_data
                else:
                    # Chuyển đổi records thành list để hiển thị với tabulate
                    table_data = [[record[col] for col in columns] for record in records]
                    
                    # In bảng dữ liệu
                    print(tabulate(table_data, headers=columns, tablefmt="pretty"))
                    print(f"Tổng số: {len(records)} bản ghi\n")
                    return table_data
                
        except Exception as e:
            logging.error(f"Lỗi khi thực thi truy vấn '{query_name}': {e}")
            return []

    def save_query_to_json(self, query_name, file_path=None):
        """
        Thực thi truy vấn và lưu kết quả vào file JSON
        
        Args:
            query_name (str): Tên của truy vấn để thực thi
            file_path (str, optional): Đường dẫn file để lưu. Nếu None, sẽ tạo tên file dựa trên tên truy vấn.
        """
        if not file_path:
            file_path = f"{query_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if not self.driver:
            logging.error("Không có kết nối Neo4j. Không thể thực thi truy vấn.")
            return
        
        if query_name not in QUERIES:
            logging.error(f"Không tìm thấy truy vấn với tên: {query_name}")
            self.list_available_queries()
            return
        
        query_info = QUERIES[query_name]
        query = query_info["query"]
        description = query_info["description"]
        
        try:
            with self.driver.session() as session:
                result = session.run(query)
                records = list(result)
                
                if not records:
                    logging.warning(f"Không có dữ liệu nào được tìm thấy cho truy vấn '{query_name}'.")
                    return
                
                # Lấy tên các cột
                columns = result.keys()
                
                # Chuyển đổi kết quả thành danh sách các dictionary
                json_data = []
                for record in records:
                    record_dict = {}
                    for col in columns:
                        record_dict[col] = record[col]
                    json_data.append(record_dict)
                
                # Ghi dữ liệu vào file JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2, cls=Neo4jEncoder)
                
                logging.info(f"Đã lưu kết quả truy vấn '{query_name}' vào file: {file_path}")
                print(f"Đã lưu kết quả vào: {file_path}")
                
        except Exception as e:
            logging.error(f"Lỗi khi thực thi và lưu truy vấn '{query_name}': {e}")

    def list_available_queries(self):
        """Hiển thị danh sách các truy vấn có sẵn."""
        print("\n=== DANH SÁCH CÁC TRUY VẤN CÓ SẴN ===\n")
        for key, value in QUERIES.items():
            print(f"- {key}: {value['description']}")
        print("\nSử dụng: python query_neo4j_data.py <tên_truy_vấn> [table|json]")
        print("Hoặc:    python query_neo4j_data.py all [table|json] (để chạy tất cả truy vấn)")
        print("Hoặc:    python query_neo4j_data.py save <tên_truy_vấn> [file_path] (để lưu vào file JSON)")

    def run_all_queries(self, output_format="table"):
        """Chạy tất cả các truy vấn có sẵn."""
        for query_name in QUERIES:
            self.execute_query(query_name, output_format)
            if output_format == "table":
                print("\n" + "-" * 80 + "\n")

def main():
    retriever = Neo4jDataRetriever(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    if not retriever.driver:
        return
    
    try:
        if len(sys.argv) < 2:
            # Không có tham số, hiển thị trợ giúp
            retriever.list_available_queries()
        elif sys.argv[1].lower() == "all":
            # Chạy tất cả các truy vấn
            output_format = "table"
            if len(sys.argv) >= 3 and sys.argv[2].lower() == "json":
                output_format = "json"
            retriever.run_all_queries(output_format)
        elif sys.argv[1].lower() == "save":
            # Lưu kết quả truy vấn vào file JSON
            if len(sys.argv) < 3:
                print("Thiếu tên truy vấn cần lưu. Ví dụ: python query_neo4j_data.py save all_students")
                retriever.list_available_queries()
            else:
                query_name = sys.argv[2]
                file_path = None
                if len(sys.argv) >= 4:
                    file_path = sys.argv[3]
                retriever.save_query_to_json(query_name, file_path)
        else:
            # Chạy truy vấn cụ thể
            query_name = sys.argv[1]
            output_format = "table"
            if len(sys.argv) >= 3 and sys.argv[2].lower() == "json":
                output_format = "json"
            retriever.execute_query(query_name, output_format)
    finally:
        retriever.close()

if __name__ == "__main__":
    main() 