#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Knowledge Nodes for Toán Lớp 1
Import trực tiếp vào Neo4j database
"""

import os
import uuid
from datetime import datetime
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class KnowledgeImporter:
    def __init__(self):
        self.driver = None
        self.connect()
    
    def connect(self):
        """Kết nối tới Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, 
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("✅ Connected to Neo4j successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Đóng kết nối"""
        if self.driver:
            self.driver.close()
            logger.info("🔒 Neo4j connection closed")
    
    def generate_uuid(self):
        """Generate unique UUID"""
        return str(uuid.uuid4())
    
    def get_knowledge_list(self):
        """Danh sách tất cả kiến thức Toán Lớp 1"""
        return [
            "Trên - Dưới, Phải - Trái, Trước - Sau, Ở giữa",
            "Hình vuông - Hình tròn - Hình tam giác - Hình chữ nhật",
            "Các số 1, 2, 3",
            "Các số 4, 5, 6", 
            "Các số 7, 8, 9",
            "Số 0",
            "Số 10",
            "Nhiều hơn - Ít hơn - Bằng nhau",
            "Lớn hơn, dấu >. Bé hơn, dấu <. Bằng nhau, dấu =",
            "Em ôn lại những gì đã học",
            "Làm quen với Phép cộng - Dấu cộng",
            "Làm quen với Phép cộng - Dấu cộng (tiếp theo)",
            "Phép cộng trong phạm vi 6",
            "Phép cộng trong phạm vi 6 (tiếp theo)",
            "Phép cộng trong phạm vi 10",
            "Phép cộng trong phạm vi 10 (tiếp theo)",
            "Khối hộp chữ nhật - Khối lập phương",
            "Làm quen với Phép trừ - Dấu trừ",
            "Phép trừ trong phạm vi 6",
            "Phép trừ trong phạm vi 6 (tiếp theo)",
            "Phép trừ trong phạm vi 10",
            "Phép trừ trong phạm vi 10 (tiếp theo)",
            "Các số 11, 12, 13, 14, 15, 16",
            "Các số 17, 18, 19, 20",
            "Các số 10, 20, 30, 40, 50, 60, 70, 80, 90",
            "Các số có hai chữ số (từ 21 đến 40)",
            "Các số có hai chữ số (từ 41 đến 70)",
            "Các số có hai chữ số (từ 71 đến 99)",
            "Các số đến 100",
            "Chục và đơn vị",
            "So sánh các số trong phạm vi 100",
            "Dài hơn - Ngắn hơn",
            "Đo độ dài",
            "Xăng-ti-mét",
            "Phép cộng dạng 14 + 3",
            "Phép trừ dạng 17 - 2",
            "Cộng, trừ các số tròn chục",
            "Phép cộng dạng 25 + 14",
            "Phép cộng dạng 25 + 4, 25 + 40",
            "Phép trừ dạng 39 – 15",
            "Phép trừ dạng 27 – 4, 63 – 40",
            "Các ngày trong tuần lễ",
            "Đồng hồ - thời gian"
        ]
    
    def check_existing_knowledge(self, session):
        """Kiểm tra Knowledge nodes đã tồn tại"""
        result = session.run("MATCH (k:Knowledge) RETURN count(k) as count")
        count = result.single()["count"]
        logger.info(f"📊 Found {count} existing Knowledge nodes")
        return count
    
    def clear_existing_knowledge(self, session):
        """Xóa tất cả Knowledge nodes cũ (nếu cần)"""
        result = session.run("MATCH (k:Knowledge) DELETE k RETURN count(k) as deleted")
        deleted = result.consume().counters.nodes_deleted
        logger.info(f"🗑️ Deleted {deleted} existing Knowledge nodes")
        return deleted
    
    def create_knowledge_node(self, session, knowledge_data):
        """Tạo một Knowledge node"""
        query = """
        CREATE (k:Knowledge {
            id: $id,
            name: $name,
            description: $description,
            order: $order,
            subject: $subject,
            grade: $grade,
            createdAt: $createdAt,
            updatedAt: $updatedAt
        })
        RETURN k
        """
        
        result = session.run(query, knowledge_data)
        return result.single()["k"]
    
    def bulk_create_knowledge(self, session, knowledge_list):
        """Tạo nhiều Knowledge nodes cùng lúc (optimized)"""
        query = """
        UNWIND $knowledge_list as knowledge
        CREATE (k:Knowledge {
            id: knowledge.id,
            name: knowledge.name,
            description: knowledge.description,
            order: knowledge.order,
            subject: knowledge.subject,
            grade: knowledge.grade,
            createdAt: knowledge.createdAt,
            updatedAt: knowledge.updatedAt
        })
        RETURN count(k) as created_count
        """
        
        result = session.run(query, knowledge_list=knowledge_list)
        return result.single()["created_count"]
    
    def import_knowledge_nodes(self, clear_existing=False, use_bulk=True):
        """Import tất cả Knowledge nodes"""
        knowledge_names = self.get_knowledge_list()
        
        # Prepare data
        knowledge_data = []
        now = datetime.now().isoformat()
        
        for i, name in enumerate(knowledge_names, 1):
            data = {
                "id": self.generate_uuid(),
                "name": name,
                "description": f"Kiến thức về: {name}",
                "order": i,
                "subject": "Toán",
                "grade": "Lớp 1",
                "createdAt": now,
                "updatedAt": now
            }
            knowledge_data.append(data)
        
        # Import to Neo4j
        with self.driver.session() as session:
            # Check existing
            existing_count = self.check_existing_knowledge(session)
            
            # Clear if requested
            if clear_existing and existing_count > 0:
                user_input = input(f"❓ Delete {existing_count} existing Knowledge nodes? (y/N): ")
                if user_input.lower() == 'y':
                    self.clear_existing_knowledge(session)
                else:
                    logger.info("⏭️ Skipping deletion, adding new nodes...")
            
            # Create nodes
            logger.info(f"📝 Creating {len(knowledge_data)} Knowledge nodes...")
            
            if use_bulk:
                # Bulk import (faster)
                try:
                    created_count = self.bulk_create_knowledge(session, knowledge_data)
                    logger.info(f"✅ Bulk created {created_count} Knowledge nodes")
                except Exception as e:
                    logger.error(f"❌ Bulk import failed: {e}")
                    logger.info("🔄 Falling back to individual creation...")
                    use_bulk = False
            
            if not use_bulk:
                # Individual import (slower but more reliable)
                created_count = 0
                errors = []
                
                for i, data in enumerate(knowledge_data, 1):
                    try:
                        node = self.create_knowledge_node(session, data)
                        logger.info(f"✅ {i:2d}. {data['name']}")
                        created_count += 1
                    except Exception as e:
                        error_msg = f"❌ {i:2d}. {data['name']} - {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                
                if errors:
                    logger.error(f"💥 {len(errors)} errors occurred:")
                    for error in errors:
                        logger.error(f"   {error}")
        
        return created_count, len(knowledge_data)
    
    def verify_import(self):
        """Kiểm tra kết quả import"""
        with self.driver.session() as session:
            # Count total
            result = session.run("MATCH (k:Knowledge) RETURN count(k) as total")
            total = result.single()["total"]
            
            # Sample some records
            result = session.run("""
                MATCH (k:Knowledge) 
                RETURN k.name as name, k.order as order 
                ORDER BY k.order 
                LIMIT 5
            """)
            
            sample = [f"{record['order']:2d}. {record['name']}" for record in result]
            
            logger.info(f"🔍 Verification:")
            logger.info(f"   Total Knowledge nodes: {total}")
            logger.info(f"   Sample records:")
            for item in sample:
                logger.info(f"      {item}")
            
            return total

def main():
    """Main function"""
    logger.info("🚀 Starting Knowledge Import for Toán Lớp 1...")
    logger.info("=" * 70)
    
    importer = None
    try:
        # Initialize importer
        importer = KnowledgeImporter()
        
        # Import knowledge nodes
        created, total = importer.import_knowledge_nodes(
            clear_existing=True,  # Set to False if you don't want to clear existing
            use_bulk=True         # Use bulk import for better performance
        )
        
        logger.info("=" * 70)
        logger.info(f"📊 Import Summary:")
        logger.info(f"   Total processed: {total}")
        logger.info(f"   Successfully created: {created}")
        
        # Verify
        logger.info("=" * 70)
        final_count = importer.verify_import()
        
        logger.info("=" * 70)
        logger.info("🎉 Import completed successfully!")
        logger.info(f"✅ {final_count} Knowledge nodes are now in Neo4j")
        
    except Exception as e:
        logger.error(f"💥 Import failed: {e}")
        return 1
    
    finally:
        if importer:
            importer.close()
    
    return 0

if __name__ == "__main__":
    exit(main())