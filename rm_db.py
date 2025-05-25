#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Database Cleaner
Xóa toàn bộ dữ liệu trong Neo4j database
"""

import os
from neo4j import GraphDatabase

def clear_neo4j_database():
    """Xóa toàn bộ dữ liệu trong Neo4j database"""
    
    # Lấy thông tin kết nối từ biến môi trường
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME") 
    password = os.getenv("NEO4J_PASSWORD")
    
    if not all([uri, username, password]):
        print("❌ Thiếu thông tin kết nối Neo4j!")
        print("Vui lòng thiết lập các biến môi trường:")
        print("  export NEO4J_URI='bolt://localhost:7687'")
        print("  export NEO4J_USERNAME='neo4j'")
        print("  export NEO4J_PASSWORD='your_password'")
        return False
    
    try:
        # Kết nối đến Neo4j
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # Kiểm tra số lượng nodes hiện tại
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            
            if node_count == 0:
                print("✅ Database đã trống, không cần xóa gì!")
                return True
            
            print(f"📊 Tìm thấy {node_count} nodes trong database")
            
            # Xác nhận xóa
            confirm = input("⚠️  Bạn có chắc chắn muốn xóa TOÀN BỘ dữ liệu? (yes/no): ").lower().strip()
            
            if confirm not in ['yes', 'y']:
                print("❌ Hủy bỏ thao tác xóa")
                return False
            
            print("🗑️ Đang xóa toàn bộ dữ liệu...")
            
            # Xóa toàn bộ dữ liệu (nodes và relationships)
            session.run("MATCH (n) DETACH DELETE n")
            
            # Kiểm tra lại
            result = session.run("MATCH (n) RETURN count(n) as count")
            remaining_count = result.single()["count"]
            
            if remaining_count == 0:
                print("✅ Đã xóa toàn bộ dữ liệu thành công!")
            else:
                print(f"⚠️ Còn lại {remaining_count} nodes chưa được xóa")
            
            # Xóa indexes và constraints (optional)
            try:
                print("🔧 Đang xóa indexes và constraints...")
                
                # Lấy danh sách constraints
                constraints_result = session.run("SHOW CONSTRAINTS")
                constraints = [record["name"] for record in constraints_result if record.get("name")]
                
                # Xóa từng constraint
                for constraint_name in constraints:
                    try:
                        session.run(f"DROP CONSTRAINT {constraint_name}")
                        print(f"  ✅ Đã xóa constraint: {constraint_name}")
                    except Exception as e:
                        print(f"  ⚠️ Không thể xóa constraint {constraint_name}: {e}")
                
                # Lấy danh sách indexes
                indexes_result = session.run("SHOW INDEXES")
                indexes = [record["name"] for record in indexes_result if record.get("name") and record.get("type") != "LOOKUP"]
                
                # Xóa từng index
                for index_name in indexes:
                    try:
                        session.run(f"DROP INDEX {index_name}")
                        print(f"  ✅ Đã xóa index: {index_name}")
                    except Exception as e:
                        print(f"  ⚠️ Không thể xóa index {index_name}: {e}")
                        
            except Exception as e:
                print(f"⚠️ Lỗi khi xóa indexes/constraints: {e}")
            
        driver.close()
        print("🎉 Hoàn thành việc dọn dẹp database!")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kết nối hoặc xóa database: {e}")
        return False

def main():
    """Hàm main"""
    print("🗑️ Neo4j Database Cleaner")
    print("=" * 40)
    
    success = clear_neo4j_database()
    
    if success:
        print("\n💡 Database đã sẵn sàng cho việc import dữ liệu mới!")
    else:
        print("\n💥 Có lỗi xảy ra trong quá trình xóa database")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())