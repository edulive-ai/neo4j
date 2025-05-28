from neo4j_module import EducationSystem

with EducationSystem() as edu:
    users_data = [
        {"id": "user_001", "name": "John Doe", "email": "john@example.com", "age": 25},
        {"id": "user_002", "name": "Jane Smith", "email": "jane@example.com", "age": 30},
        {"name": "Bob Wilson", "email": "bob@example.com"}  # Không có ID -> tự generate
        ]

    result = edu.bulk_create_users(users_data)
    print(result)
