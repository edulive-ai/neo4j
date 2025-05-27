#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk Link Users to Knowledge Script
Tạo relationships giữa tất cả users và tất cả knowledge nodes
"""

import requests
import json
import random

# API Configuration
BASE_URL = "https://9a3c-14-231-173-228.ngrok-free.app"

# Extract User IDs
user_ids = [
    "511f5100-1c1a-4018-8ce1-ae3cbb0fcc9e",  # Bùi Thị Lan
    "d326edac-8248-4c5e-98c6-aefa8b834829",  # Hoàng Văn Em
    "8ac8cdc3-5ed1-40ee-bbca-53306164d5f3",  # Lê Văn Cường
    "767a8503-0233-4501-9c29-94916808a1ba",  # Nguyễn Văn An
    "878a9e2c-ddf6-4e86-812b-929c73dae665",  # Phạm Thị Dung
    "bc388cbe-4b19-4df9-a123-a92d77ba0201",  # Trần Thị Bình
    "b84adec9-c450-4bbc-b1cf-208d82a1248f",  # Vũ Thị Hoa
    "b51e0f10-5a71-4ef8-a07f-dde47a717532"   # Đặng Văn Khoa
]

# Extract Knowledge IDs
knowledge_ids = [
    "b3ba9891-096b-4219-9692-0569abe17321",  # Trên - Dưới, Phải - Trái
    "ed613e7c-6e99-4d93-8a8b-820f4d2e1db7",  # Hình vuông - Hình tròn
    "e145588f-bc4f-4d7f-8d50-5dfddfa924e7",  # Các số 1, 2, 3
    "6242e69e-1161-4742-8bc9-05b01390d4d6",  # Các số 4, 5, 6
    "2f012143-90f7-4ed6-b039-2b33480d4a19",  # Các số 7, 8, 9
    "93012727-4b06-4c92-8647-e8ac48e8897d",  # Số 0
    "42aacd2e-8561-442c-a710-1c833cbb5e09",  # Số 10
    "a04d34fe-801c-4632-b7ee-09ab82ce5222",  # Nhiều hơn - Ít hơn
    "8f28f9e0-a7ad-4b9d-bb41-a520becb713e",  # Lớn hơn, dấu >
    "348885a4-e583-451a-8eb7-d88657ac271e",  # Em ôn lại những gì đã học
    "3fb32ed7-35f9-4c46-b5b8-13f42b5ade42",  # Làm quen với Phép cộng
    "8468aaa6-47ef-4438-920b-e0d130bd7a24",  # Phép cộng (tiếp theo)
    "a2db7b20-f224-4699-9095-351a7598b348",  # Phép cộng trong phạm vi 6
    "caca041b-7345-4965-8d32-81608b9ebc7c",  # Phép cộng phạm vi 6 (tiếp)
    "462f38a0-f01d-4283-82d5-89db8a03a92b",  # Phép cộng trong phạm vi 10
    "244ed907-8803-4fbb-8c24-d1d1ae846455",  # Phép cộng phạm vi 10 (tiếp)
    "17dd2a9e-95f6-4bbc-a999-ad94b08053d6",  # Khối hộp chữ nhật
    "c73627eb-f704-45c6-89e8-0c7084dcdf49",  # Làm quen với Phép trừ
    "6324b189-efed-45f2-9d73-9b681d2064a8",  # Phép trừ trong phạm vi 6
    "b798c7c0-3eb4-4aa2-a136-0862d42f92bd",  # Phép trừ phạm vi 6 (tiếp)
    "d9e509fe-9790-4e08-9c4c-895b7627ad15",  # Phép trừ trong phạm vi 10
    "8fb0bb57-90da-423a-9e20-713371cce4ef",  # Phép trừ phạm vi 10 (tiếp)
    "4eea98a4-425a-403e-89cf-39d4e6d31a2f",  # Các số 11-16
    "ac25c520-7da3-4998-b3f1-322ac724b2f0",  # Các số 17-20
    "63ade7ec-bb02-4b47-84c7-ebc256e5bcfb",  # Các số tròn chục
    "4ad72a97-d94e-4f29-b4d1-393e8a8e133b",  # Số hai chữ số 21-40
    "0634a389-bc11-4e2d-b9f8-cd9ece2bdd81",  # Số hai chữ số 41-70
    "d3c05eff-4dd8-4b21-bfd9-47ca12222116",  # Số hai chữ số 71-99
    "d30194ef-7a14-4a4d-accf-378bc1dba048",  # Các số đến 100
    "a811315b-7b28-48d7-bf7d-dca1d3fe59b5",  # Chục và đơn vị
    "c47723b8-927e-4830-ab3d-aeed0199c8f8",  # So sánh số trong phạm vi 100
    "4d1ca1be-2028-43dc-acf2-8583ea07132b",  # Dài hơn - Ngắn hơn
    "4c156ee2-0f4b-4091-8d84-3b99965897bc",  # Đo độ dài
    "a570ab88-19e0-4368-a954-e82587fc01c4",  # Xăng-ti-mét
    "ea6c475b-1b0e-4ea8-8ad6-8cbf842a8460",  # Phép cộng dạng 14 + 3
    "7a5ea2f4-4c96-4349-8d65-b2a922d0f23d",  # Phép trừ dạng 17 - 2
    "b8e106da-aaa0-41c8-bee4-1b4c7974c3c9",  # Cộng, trừ số tròn chục
    "3656c2fe-a712-44b8-8f3d-edc4b57416b3",  # Phép cộng dạng 25 + 14
    "774e4e88-efbe-44c5-9a2a-bd762cc5223a",  # Phép cộng 25 + 4, 25 + 40
    "0b5faa0d-c608-41e0-81ad-776441b42447",  # Phép trừ dạng 39 – 15
    "3c005cbf-32e9-4902-94c6-8a13346c075c",  # Phép trừ 27 – 4, 63 – 40
    "243975de-e61d-432c-bf77-d3c0d70f4a59",  # Các ngày trong tuần lễ
    "4b15b616-4b53-45c3-bc54-ffa391dc2ba5"   # Đồng hồ - thời gian
]

def generate_realistic_progress_data():
    """Tạo dữ liệu progress realistic cho từng knowledge"""
    # Các knowledge cơ bản (đầu chương trình) có progress cao hơn
    # Các knowledge nâng cao (cuối chương trình) có progress thấp hơn
    
    progress_patterns = {
        # Knowledge cơ bản (order 1-10): progress cao
        "basic": {"min": 60, "max": 100, "statuses": ["completed", "mastered", "reviewing"]},
        
        # Knowledge trung bình (order 11-25): progress trung bình
        "intermediate": {"min": 30, "max": 85, "statuses": ["learning", "completed", "reviewing"]},
        
        # Knowledge nâng cao (order 26-43): progress thấp
        "advanced": {"min": 0, "max": 60, "statuses": ["learning", "reviewing"]}
    }
    
    def get_pattern_for_order(order):
        if order <= 10:
            return progress_patterns["basic"]
        elif order <= 25:
            return progress_patterns["intermediate"]
        else:
            return progress_patterns["advanced"]
    
    return get_pattern_for_order

def create_all_relationships():
    """Tạo tất cả relationships giữa users và knowledge"""
    
    # Tạo generator function cho progress patterns
    get_progress_pattern = generate_realistic_progress_data()
    
    # Tạo links array
    links = []
    
    for user_id in user_ids:
        for i, knowledge_id in enumerate(knowledge_ids, 1):
            # Lấy pattern dựa trên order của knowledge
            pattern = get_progress_pattern(i)
            
            # Random progress và status theo pattern
            progress = random.randint(pattern["min"], pattern["max"])
            status = random.choice(pattern["statuses"])
            
            # Tạo link object
            link = {
                "user_id": user_id,
                "knowledge_id": knowledge_id,
                "status": status,
                "progress": progress
            }
            
            links.append(link)
    
    return links

def bulk_create_relationships(links):
    """Gửi bulk request để tạo relationships"""
    
    url = f"{BASE_URL}/api/v1/users/bulk/knowledge"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "links": links
    }
    
    try:
        print(f"🚀 Sending bulk request with {len(links)} relationships...")
        print(f"📊 That's {len(user_ids)} users × {len(knowledge_ids)} knowledge = {len(links)} total relationships")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Success! {result['total_created']} relationships created")
            print(f"📈 Processing summary:")
            print(f"   - Total processed: {result['total_processed']}")
            print(f"   - Successfully created: {result['total_created']}")
            print(f"   - Errors: {result['total_errors']}")
            
            if result['errors']:
                print(f"⚠️ Errors encountered:")
                for error in result['errors'][:5]:  # Show first 5 errors
                    print(f"   - {error}")
                if len(result['errors']) > 5:
                    print(f"   ... and {len(result['errors']) - 5} more errors")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def create_sample_relationships():
    """Tạo sample relationships cho testing (chỉ 1 user với 5 knowledge đầu)"""
    
    print("🧪 Creating sample relationships for testing...")
    
    # Chỉ lấy 1 user và 5 knowledge đầu
    sample_user = user_ids[0]  # Bùi Thị Lan
    sample_knowledge = knowledge_ids[:5]  # 5 knowledge đầu
    
    links = []
    for i, knowledge_id in enumerate(sample_knowledge, 1):
        link = {
            "user_id": sample_user,
            "knowledge_id": knowledge_id,
            "status": "learning",
            "progress": i * 20  # 20, 40, 60, 80, 100
        }
        links.append(link)
    
    bulk_create_relationships(links)

def verify_existing_relationships():
    """Kiểm tra relationships đã tồn tại"""
    
    print("🔍 Checking existing relationships...")
    
    url = f"{BASE_URL}/api/v1/users-knowledge/analytics"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            stats = result.get('overall_stats', {})
            
            print(f"📊 Current system stats:")
            print(f"   - Users with knowledge: {stats.get('total_users_learning', 0)}")
            print(f"   - Total relationships: {stats.get('total_relationships', 0)}")
            print(f"   - Average progress: {stats.get('avg_progress', 0):.1f}%")
            
            return stats.get('total_relationships', 0)
        else:
            print(f"❌ Failed to get analytics: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"💥 Error checking analytics: {e}")
        return 0

def main():
    """Main function với menu options"""
    
    print("🎓 User-Knowledge Relationship Creator")
    print("=" * 50)
    
    # Check existing relationships
    existing_count = verify_existing_relationships()
    
    print("\nOptions:")
    print("1. Create sample relationships (1 user × 5 knowledge)")
    print("2. Create ALL relationships (8 users × 43 knowledge = 344 total)")
    print("3. Check analytics only")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        create_sample_relationships()
        
    elif choice == "2":
        if existing_count > 0:
            confirm = input(f"⚠️ Found {existing_count} existing relationships. Continue? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                return
        
        print("\n🚀 Creating ALL relationships...")
        links = create_all_relationships()
        bulk_create_relationships(links)
        
        # Verify final result
        print("\n🔍 Final verification:")
        verify_existing_relationships()
        
    elif choice == "3":
        verify_existing_relationships()
        
    elif choice == "4":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()