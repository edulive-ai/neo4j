# -*- coding: utf-8 -*-
"""
Neo4j Educational API - Correct Structure
Based on: Subject → TypeBook → Chapter → Lesson → Question
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class Neo4jEducationAPI:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USERNAME", "neo4j") 
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        self.connect()
        
    def connect(self):
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("✅ Connected to Neo4j")
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            raise
    
    def close(self):
        if self.driver:
            self.driver.close()

neo4j_api = Neo4jEducationAPI()

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({'error': str(e), 'success': False}), 500
    return decorated_function

def validate_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_type != 'application/json':
            return jsonify({'error': 'Content-Type must be application/json', 'success': False}), 400
        try:
            request.get_json(force=True)
        except:
            return jsonify({'error': 'Invalid JSON', 'success': False}), 400
        return f(*args, **kwargs)
    return decorated_function

# ==================== HEALTH CHECK ====================

@app.route('/api/v1/health', methods=['GET'])
@handle_errors
def health_check():
    """Check API health"""
    with neo4j_api.driver.session() as session:
        session.run("RETURN 1")
    return jsonify({'status': 'healthy', 'success': True})

# ==================== HIERARCHY MANAGEMENT ====================

@app.route('/api/v1/subjects', methods=['GET'])
@handle_errors
def get_subjects():
    """Get all subjects"""
    with neo4j_api.driver.session() as session:
        result = session.run("MATCH (s:Subject) RETURN s ORDER BY s.name")
        subjects = [dict(record["s"].items()) for record in result]
    return jsonify({'subjects': subjects, 'count': len(subjects), 'success': True})

@app.route('/api/v1/typebooks', methods=['GET'])
@handle_errors
def get_typebooks():
    """Get all typebooks with subject info"""
    subject_id = request.args.get('subject_id')
    
    with neo4j_api.driver.session() as session:
        if subject_id:
            result = session.run("""
                MATCH (s:Subject {id: $subject_id})<-[:BELONGS_TO_SUBJECT]-(t:TypeBook)
                RETURN t, s.name as subject_name
                ORDER BY t.name
            """, subject_id=subject_id)
        else:
            result = session.run("""
                MATCH (s:Subject)<-[:BELONGS_TO_SUBJECT]-(t:TypeBook)
                RETURN t, s.name as subject_name
                ORDER BY s.name, t.name
            """)
        
        typebooks = []
        for record in result:
            typebook = dict(record["t"].items())
            typebook['subject_name'] = record['subject_name']
            typebooks.append(typebook)
    
    return jsonify({'typebooks': typebooks, 'count': len(typebooks), 'success': True})

@app.route('/api/v1/chapters', methods=['GET'])
@handle_errors
def get_chapters():
    """Get all chapters with typebook info"""
    typebook_id = request.args.get('typebook_id')
    
    with neo4j_api.driver.session() as session:
        if typebook_id:
            result = session.run("""
                MATCH (t:TypeBook {id: $typebook_id})<-[:BELONGS_TO_TYPE_BOOK]-(c:Chapter)
                RETURN c, t.name as typebook_name
                ORDER BY c.order
            """, typebook_id=typebook_id)
        else:
            result = session.run("""
                MATCH (t:TypeBook)<-[:BELONGS_TO_TYPE_BOOK]-(c:Chapter)
                RETURN c, t.name as typebook_name
                ORDER BY t.name, c.order
            """)
        
        chapters = []
        for record in result:
            chapter = dict(record["c"].items())
            chapter['typebook_name'] = record['typebook_name']
            chapters.append(chapter)
    
    return jsonify({'chapters': chapters, 'count': len(chapters), 'success': True})

@app.route('/api/v1/lessons', methods=['GET'])
@handle_errors
def get_lessons():
    """Get all lessons with chapter info"""
    chapter_id = request.args.get('chapter_id')
    
    with neo4j_api.driver.session() as session:
        if chapter_id:
            result = session.run("""
                MATCH (c:Chapter {id: $chapter_id})<-[:BELONGS_TO_CHAPTER]-(l:Lesson)
                RETURN l, c.name as chapter_name
                ORDER BY l.order
            """, chapter_id=chapter_id)
        else:
            result = session.run("""
                MATCH (c:Chapter)<-[:BELONGS_TO_CHAPTER]-(l:Lesson)
                RETURN l, c.name as chapter_name
                ORDER BY c.order, l.order
            """)
        
        lessons = []
        for record in result:
            lesson = dict(record["l"].items())
            lesson['chapter_name'] = record['chapter_name']
            lessons.append(lesson)
    
    return jsonify({'lessons': lessons, 'count': len(lessons), 'success': True})

# ==================== USERS SECTION ====================

@app.route('/api/v1/users', methods=['GET'])
@handle_errors
def get_users():
    """Get all users"""
    with neo4j_api.driver.session() as session:
        result = session.run("MATCH (u:User) RETURN u ORDER BY u.name")
        users = [dict(record["u"].items()) for record in result]
    
    return jsonify({'users': users, 'count': len(users), 'success': True})

@app.route('/api/v1/users', methods=['POST'])
@handle_errors
@validate_json
def create_user():
    """Create new user"""
    data = request.get_json()
    
    if not all(field in data for field in ['name', 'email']):
        return jsonify({'error': 'name and email required', 'success': False}), 400
    
    with neo4j_api.driver.session() as session:
        # Check if email exists
        existing = session.run("MATCH (u:User {email: $email}) RETURN u", email=data['email'])
        if existing.single():
            return jsonify({'error': 'Email already exists', 'success': False}), 409
        
        # Create user
        user_data = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'email': data['email'],
            'age': data.get('age', 7),
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        result = session.run("""
            CREATE (u:User {
                id: $id, name: $name, email: $email, age: $age, 
                createdAt: $createdAt, updatedAt: $updatedAt
            })
            RETURN u
        """, user_data)
        
        created_user = dict(result.single()["u"].items())
    
    return jsonify({'message': 'User created', 'user': created_user, 'success': True}), 201

@app.route('/api/v1/users/bulk', methods=['POST'])
@handle_errors
@validate_json
def import_users_optimized():
    """Optimized bulk import for users"""
    data = request.get_json()
    
    if 'users' not in data:
        return jsonify({'error': 'users array required', 'success': False}), 400
    
    batch_size = data.get('batch_size', 1000)  # Process in batches
    users_data = data['users']
    
    created_users = []
    errors = []
    
    with neo4j_api.driver.session() as session:
        with session.begin_transaction() as tx:
            try:
                # Validate all users first
                valid_users = []
                for i, user in enumerate(users_data):
                    if not all(field in user for field in ['name', 'email']):
                        errors.append(f'User {i}: Missing name or email')
                        continue
                    
                    # Check email format
                    if '@' not in user['email']:
                        errors.append(f'User {i}: Invalid email format')
                        continue
                    
                    user_data = {
                        'id': str(uuid.uuid4()),
                        'name': user['name'].strip(),
                        'email': user['email'].strip().lower(),
                        'age': user.get('age', 7),
                        'createdAt': datetime.now().isoformat(),
                        'updatedAt': datetime.now().isoformat()
                    }
                    valid_users.append(user_data)
                
                if not valid_users:
                    return jsonify({'error': 'No valid users to import', 'errors': errors, 'success': False}), 400
                
                # Check for existing emails in batch
                existing_emails = []
                if valid_users:
                    email_list = [user['email'] for user in valid_users]
                    existing_result = tx.run("""
                        MATCH (u:User) 
                        WHERE u.email IN $email_list 
                        RETURN u.email as email
                    """, email_list=email_list)
                    existing_emails = [record['email'] for record in existing_result]
                
                # Filter out existing emails
                new_users = []
                for user in valid_users:
                    if user['email'] in existing_emails:
                        errors.append(f'Email {user["email"]} already exists')
                    else:
                        new_users.append(user)
                
                # Bulk create users in batches
                for i in range(0, len(new_users), batch_size):
                    batch = new_users[i:i + batch_size]
                    
                    # Single query to create multiple users
                    result = tx.run("""
                        UNWIND $users as user
                        CREATE (u:User {
                            id: user.id, name: user.name, email: user.email, 
                            age: user.age, createdAt: user.createdAt, updatedAt: user.updatedAt
                        })
                        RETURN u
                    """, users=batch)
                    
                    batch_created = [dict(record["u"].items()) for record in result]
                    created_users.extend(batch_created)
                
                tx.commit()
                
            except Exception as e:
                tx.rollback()
                return jsonify({'error': f'Transaction failed: {str(e)}', 'success': False}), 500
    
    return jsonify({
        'message': f'{len(created_users)} users imported successfully (optimized)',
        'created_users': created_users,
        'total_processed': len(users_data),
        'total_created': len(created_users),
        'total_errors': len(errors),
        'errors': errors,
        'success': len(created_users) > 0
    }), 201

@app.route('/api/v1/questions/bulk', methods=['POST'])
@handle_errors
@validate_json
def import_questions_optimized():
    """Optimized bulk import for questions with relationships"""
    data = request.get_json()
    
    if 'questions' not in data:
        return jsonify({'error': 'questions array required', 'success': False}), 400
    
    batch_size = data.get('batch_size', 500)  # Smaller batch for relationships
    questions_data = data['questions']
    
    created_questions = []
    errors = []
    
    with neo4j_api.driver.session() as session:
        with session.begin_transaction() as tx:
            try:
                # Validate and prepare questions
                valid_questions = []
                lesson_ids = set()
                
                for i, question in enumerate(questions_data):
                    required_fields = ['lesson_id', 'title', 'content', 'correct_answer', 'difficulty', 'page']
                    missing_fields = [field for field in required_fields if field not in question]
                    if missing_fields:
                        errors.append(f'Question {i}: Missing {missing_fields}')
                        continue
                    
                    question_data = {
                        'id': str(uuid.uuid4()),
                        'lesson_id': question['lesson_id'],  # Store for relationship
                        'title': question['title'],
                        'content': question['content'],
                        'correct_answer': question['correct_answer'],
                        'image_question': question.get('image_question', ''),
                        'image_answer': question.get('image_answer', ''),
                        'difficulty': question['difficulty'],
                        'page': question['page'],
                        'createdAt': datetime.now().isoformat(),
                        'updatedAt': datetime.now().isoformat()
                    }
                    valid_questions.append(question_data)
                    lesson_ids.add(question['lesson_id'])
                
                if not valid_questions:
                    return jsonify({'error': 'No valid questions to import', 'errors': errors, 'success': False}), 400
                
                # Validate all lesson_ids exist in batch
                existing_lessons = set()
                if lesson_ids:
                    lesson_result = tx.run("""
                        MATCH (l:Lesson) 
                        WHERE l.id IN $lesson_ids 
                        RETURN l.id as id
                    """, lesson_ids=list(lesson_ids))
                    existing_lessons = {record['id'] for record in lesson_result}
                
                # Filter questions with valid lessons
                final_questions = []
                for question in valid_questions:
                    if question['lesson_id'] not in existing_lessons:
                        errors.append(f'Lesson {question["lesson_id"]} not found for question {question["title"]}')
                    else:
                        final_questions.append(question)
                
                # Bulk create questions and relationships in batches
                for i in range(0, len(final_questions), batch_size):
                    batch = final_questions[i:i + batch_size]
                    
                    # Create questions
                    question_result = tx.run("""
                        UNWIND $questions as q
                        CREATE (question:Question {
                            id: q.id, title: q.title, content: q.content, 
                            correct_answer: q.correct_answer, image_question: q.image_question,
                            image_answer: q.image_answer, difficulty: q.difficulty, 
                            page: q.page, createdAt: q.createdAt, updatedAt: q.updatedAt
                        })
                        RETURN question
                    """, questions=batch)
                    
                    batch_created = [dict(record["question"].items()) for record in question_result]
                    created_questions.extend(batch_created)
                    
                    # Create relationships in batch
                    relationship_data = [{'question_id': q['id'], 'lesson_id': q['lesson_id']} for q in batch]
                    tx.run("""
                        UNWIND $relationships as rel
                        MATCH (l:Lesson {id: rel.lesson_id})
                        MATCH (q:Question {id: rel.question_id})
                        CREATE (q)-[:BELONGS_TO_LESSON]->(l)
                    """, relationships=relationship_data)
                
                tx.commit()
                
            except Exception as e:
                tx.rollback()
                return jsonify({'error': f'Transaction failed: {str(e)}', 'success': False}), 500
    
    return jsonify({
        'message': f'{len(created_questions)} questions imported with relationships (optimized)',
        'created_questions': created_questions,
        'total_processed': len(questions_data),
        'total_created': len(created_questions),
        'total_errors': len(errors),
        'errors': errors,
        'performance': {
            'batch_size': batch_size,
            'batches_processed': (len(final_questions) // batch_size) + 1
        },
        'success': len(created_questions) > 0
    }), 201

@app.route('/api/v1/answers/bulk', methods=['POST'])
@handle_errors
@validate_json
def import_answers_optimized():
    """Optimized bulk import for answers with dual relationships"""
    data = request.get_json()
    
    if 'answers' not in data:
        return jsonify({'error': 'answers array required', 'success': False}), 400
    
    batch_size = data.get('batch_size', 500)
    answers_data = data['answers']
    
    created_answers = []
    errors = []
    
    with neo4j_api.driver.session() as session:
        with session.begin_transaction() as tx:
            try:
                # Validate and prepare answers
                valid_answers = []
                user_ids = set()
                question_ids = set()
                
                for i, answer in enumerate(answers_data):
                    required_fields = ['user_id', 'question_id', 'student_answer', 'is_correct']
                    missing_fields = [field for field in required_fields if field not in answer]
                    if missing_fields:
                        errors.append(f'Answer {i}: Missing {missing_fields}')
                        continue
                    
                    now = datetime.now().isoformat()
                    answer_data = {
                        'id': str(uuid.uuid4()),
                        'user_id': answer['user_id'],
                        'question_id': answer['question_id'],
                        'student_answer': answer['student_answer'],
                        'is_correct': answer['is_correct'],
                        'start_time': answer.get('start_time', now),
                        'completion_time': answer.get('completion_time', now),
                        'duration_seconds': answer.get('duration_seconds', 0),
                        'createdAt': now,
                        'updatedAt': now
                    }
                    valid_answers.append(answer_data)
                    user_ids.add(answer['user_id'])
                    question_ids.add(answer['question_id'])
                
                if not valid_answers:
                    return jsonify({'error': 'No valid answers to import', 'errors': errors, 'success': False}), 400
                
                # Validate all user_ids and question_ids exist
                existing_users = set()
                existing_questions = set()
                
                if user_ids:
                    user_result = tx.run("MATCH (u:User) WHERE u.id IN $user_ids RETURN u.id as id", user_ids=list(user_ids))
                    existing_users = {record['id'] for record in user_result}
                
                if question_ids:
                    question_result = tx.run("MATCH (q:Question) WHERE q.id IN $question_ids RETURN q.id as id", question_ids=list(question_ids))
                    existing_questions = {record['id'] for record in question_result}
                
                # Filter answers with valid users and questions
                final_answers = []
                for answer in valid_answers:
                    if answer['user_id'] not in existing_users:
                        errors.append(f'User {answer["user_id"]} not found')
                        continue
                    if answer['question_id'] not in existing_questions:
                        errors.append(f'Question {answer["question_id"]} not found')
                        continue
                    final_answers.append(answer)
                
                # Bulk create answers and relationships
                for i in range(0, len(final_answers), batch_size):
                    batch = final_answers[i:i + batch_size]
                    
                    # Create answers
                    answer_result = tx.run("""
                        UNWIND $answers as a
                        CREATE (answer:Answer {
                            id: a.id, student_answer: a.student_answer, is_correct: a.is_correct,
                            start_time: a.start_time, completion_time: a.completion_time,
                            duration_seconds: a.duration_seconds, 
                            createdAt: a.createdAt, updatedAt: a.updatedAt
                        })
                        RETURN answer
                    """, answers=batch)
                    
                    batch_created = [dict(record["answer"].items()) for record in answer_result]
                    created_answers.extend(batch_created)
                    
                    # Create User-[:ANSWERED]->Answer relationships
                    user_relationships = [{'answer_id': a['id'], 'user_id': a['user_id']} for a in batch]
                    tx.run("""
                        UNWIND $relationships as rel
                        MATCH (u:User {id: rel.user_id})
                        MATCH (a:Answer {id: rel.answer_id})
                        CREATE (u)-[:ANSWERED]->(a)
                    """, relationships=user_relationships)
                    
                    # Create Answer-[:ANSWERS_QUESTION]->Question relationships
                    question_relationships = [{'answer_id': a['id'], 'question_id': a['question_id']} for a in batch]
                    tx.run("""
                        UNWIND $relationships as rel
                        MATCH (q:Question {id: rel.question_id})
                        MATCH (a:Answer {id: rel.answer_id})
                        CREATE (a)-[:ANSWERS_QUESTION]->(q)
                    """, relationships=question_relationships)
                
                tx.commit()
                
            except Exception as e:
                tx.rollback()
                return jsonify({'error': f'Transaction failed: {str(e)}', 'success': False}), 500
    
    return jsonify({
        'message': f'{len(created_answers)} answers imported with dual relationships (optimized)',
        'created_answers': created_answers,
        'total_processed': len(answers_data),
        'total_created': len(created_answers),
        'total_errors': len(errors),
        'errors': errors,
        'performance': {
            'batch_size': batch_size,
            'batches_processed': (len(final_answers) // batch_size) + 1
        },
        'success': len(created_answers) > 0
    }), 201

@app.route('/api/v1/questions', methods=['GET'])
@handle_errors
def get_questions():
    """Get all questions with full hierarchy"""
    lesson_id = request.args.get('lesson_id')
    chapter_id = request.args.get('chapter_id')
    
    with neo4j_api.driver.session() as session:
        if lesson_id:
            result = session.run("""
                MATCH (q:Question)-[:BELONGS_TO_LESSON]->(l:Lesson {id: $lesson_id})
                MATCH (l)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
                MATCH (c)-[:BELONGS_TO_TYPE_BOOK]->(t:TypeBook)
                MATCH (t)-[:BELONGS_TO_SUBJECT]->(s:Subject)
                RETURN q, l.name as lesson_name, c.name as chapter_name, 
                       t.name as typebook_name, s.name as subject_name
                ORDER BY q.page
            """, lesson_id=lesson_id)
        elif chapter_id:
            result = session.run("""
                MATCH (q:Question)-[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter {id: $chapter_id})
                MATCH (c)-[:BELONGS_TO_TYPE_BOOK]->(t:TypeBook)
                MATCH (t)-[:BELONGS_TO_SUBJECT]->(s:Subject)
                RETURN q, l.name as lesson_name, c.name as chapter_name, 
                       t.name as typebook_name, s.name as subject_name
                ORDER BY l.order, q.page
            """, chapter_id=chapter_id)
        else:
            result = session.run("""
                MATCH (q:Question)-[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
                MATCH (c)-[:BELONGS_TO_TYPE_BOOK]->(t:TypeBook)
                MATCH (t)-[:BELONGS_TO_SUBJECT]->(s:Subject)
                RETURN q, l.name as lesson_name, c.name as chapter_name, 
                       t.name as typebook_name, s.name as subject_name
                ORDER BY s.name, t.name, c.order, l.order, q.page
            """)
        
        questions = []
        for record in result:
            question = dict(record["q"].items())
            question['lesson_name'] = record['lesson_name']
            question['chapter_name'] = record['chapter_name']
            question['typebook_name'] = record['typebook_name']
            question['subject_name'] = record['subject_name']
            questions.append(question)
    
    return jsonify({'questions': questions, 'count': len(questions), 'success': True})
# ==================== EXPORT DATA ====================

@app.route('/api/v1/export', methods=['GET'])
@handle_errors
def export_data():
    """Export all data with full hierarchy"""
    with neo4j_api.driver.session() as session:
        # Get users
        users_result = session.run("MATCH (u:User) RETURN u")
        users = [dict(record["u"].items()) for record in users_result]
        
        # Get questions with full hierarchy
        questions_result = session.run("""
            MATCH (q:Question)-[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
            MATCH (c)-[:BELONGS_TO_TYPE_BOOK]->(t:TypeBook)
            MATCH (t)-[:BELONGS_TO_SUBJECT]->(s:Subject)
            RETURN q, l.name as lesson_name, c.name as chapter_name, 
                   t.name as typebook_name, s.name as subject_name
        """)
        
        questions = []
        for record in questions_result:
            question = dict(record["q"].items())
            question['lesson_name'] = record['lesson_name']
            question['chapter_name'] = record['chapter_name']
            question['typebook_name'] = record['typebook_name']
            question['subject_name'] = record['subject_name']
            questions.append(question)
        
        # Get answers with full context
        answers_result = session.run("""
            MATCH (u:User)-[:ANSWERED]->(a:Answer)-[:ANSWERS_QUESTION]->(q:Question)
            MATCH (q)-[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
            RETURN a, u.id as user_id, q.id as question_id,
                   u.name as student_name, q.title as question_title,
                   l.name as lesson_name, c.name as chapter_name
        """)
        
        answers = []
        for record in answers_result:
            answer = dict(record["a"].items())
            answer['user_id'] = record['user_id']
            answer['question_id'] = record['question_id']
            answer['student_name'] = record['student_name']
            answer['question_title'] = record['question_title']
            answer['lesson_name'] = record['lesson_name']
            answer['chapter_name'] = record['chapter_name']
            answers.append(answer)
    
    return jsonify({
        'users': users,
        'questions': questions,
        'answers': answers,
        'summary': {
            'total_users': len(users),
            'total_questions': len(questions),
            'total_answers': len(answers)
        },
        'success': True
    })

# ==================== TREE STRUCTURE API ====================

@app.route('/api/v1/tree', methods=['GET'])
@handle_errors
def get_tree_structure():
    """Get complete tree structure with all IDs"""
    include_users = request.args.get('include_users', 'true').lower() == 'true'
    include_questions = request.args.get('include_questions', 'true').lower() == 'true'
    
    with neo4j_api.driver.session() as session:
        # Get hierarchy structure
        hierarchy_query = """
        MATCH (s:Subject)<-[:BELONGS_TO_SUBJECT]-(t:TypeBook)<-[:BELONGS_TO_TYPE_BOOK]-(c:Chapter)<-[:BELONGS_TO_CHAPTER]-(l:Lesson)
        OPTIONAL MATCH (l)<-[:BELONGS_TO_LESSON]-(q:Question)
        RETURN s.id as subject_id, s.name as subject_name,
               t.id as typebook_id, t.name as typebook_name,
               c.id as chapter_id, c.name as chapter_name, c.order as chapter_order,
               l.id as lesson_id, l.name as lesson_name, l.order as lesson_order,
               collect({id: q.id, title: q.title, page: q.page}) as questions
        ORDER BY s.name, t.name, c.order, l.order
        """
        
        hierarchy_result = session.run(hierarchy_query)
        
        # Build tree structure
        tree = {}
        
        for record in hierarchy_result:
            subject_id = record['subject_id']
            typebook_id = record['typebook_id']
            chapter_id = record['chapter_id']
            lesson_id = record['lesson_id']
            
            # Initialize subject if not exists
            if subject_id not in tree:
                tree[subject_id] = {
                    'id': subject_id,
                    'name': record['subject_name'],
                    'type': 'subject',
                    'typebooks': {}
                }
            
            # Initialize typebook if not exists
            if typebook_id not in tree[subject_id]['typebooks']:
                tree[subject_id]['typebooks'][typebook_id] = {
                    'id': typebook_id,
                    'name': record['typebook_name'],
                    'type': 'typebook',
                    'chapters': {}
                }
            
            # Initialize chapter if not exists
            if chapter_id not in tree[subject_id]['typebooks'][typebook_id]['chapters']:
                tree[subject_id]['typebooks'][typebook_id]['chapters'][chapter_id] = {
                    'id': chapter_id,
                    'name': record['chapter_name'],
                    'order': record['chapter_order'],
                    'type': 'chapter',
                    'lessons': {}
                }
            
            # Add lesson
            tree[subject_id]['typebooks'][typebook_id]['chapters'][chapter_id]['lessons'][lesson_id] = {
                'id': lesson_id,
                'name': record['lesson_name'],
                'order': record['lesson_order'],
                'type': 'lesson'
            }
            
            # Add questions if requested
            if include_questions:
                questions = [q for q in record['questions'] if q['id'] is not None]
                tree[subject_id]['typebooks'][typebook_id]['chapters'][chapter_id]['lessons'][lesson_id]['questions'] = questions
        
        # Convert nested dicts to arrays for cleaner JSON
        clean_tree = []
        for subject in tree.values():
            subject['typebooks'] = list(subject['typebooks'].values())
            for typebook in subject['typebooks']:
                typebook['chapters'] = list(typebook['chapters'].values())
                for chapter in typebook['chapters']:
                    chapter['lessons'] = list(chapter['lessons'].values())
            clean_tree.append(subject)
        
        # Get users if requested
        users = []
        if include_users:
            users_result = session.run("MATCH (u:User) RETURN u.id as id, u.name as name, u.email as email ORDER BY u.name")
            users = [dict(record) for record in users_result]
        
        return jsonify({
            'tree_structure': clean_tree,
            'users': users if include_users else [],
            'summary': {
                'total_subjects': len(clean_tree),
                'total_users': len(users) if include_users else 0,
                'include_users': include_users,
                'include_questions': include_questions
            },
            'success': True
        })
# ==================== USER-KNOWLEDGE RELATIONSHIP API ====================

@app.route('/api/v1/knowledge', methods=['GET'])
@handle_errors
def get_knowledge():
    """Get all knowledge nodes"""
    subject = request.args.get('subject')
    grade = request.args.get('grade')
    
    with neo4j_api.driver.session() as session:
        # Build query with optional filters
        query = "MATCH (k:Knowledge)"
        conditions = []
        params = {}
        
        if subject:
            conditions.append("k.subject = $subject")
            params['subject'] = subject
        
        if grade:
            conditions.append("k.grade = $grade")
            params['grade'] = grade
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " RETURN k ORDER BY k.order"
        
        result = session.run(query, params)
        knowledge_list = [dict(record["k"].items()) for record in result]
    
    return jsonify({
        'knowledge': knowledge_list, 
        'count': len(knowledge_list), 
        'filters': {'subject': subject, 'grade': grade},
        'success': True
    })

@app.route('/api/v1/knowledge', methods=['POST'])
@handle_errors
@validate_json
def create_knowledge():
    """Create new knowledge node"""
    data = request.get_json()
    
    required_fields = ['name', 'subject', 'grade']
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Required fields: {required_fields}', 'success': False}), 400
    
    with neo4j_api.driver.session() as session:
        # Check if knowledge with same name already exists
        existing = session.run("""
            MATCH (k:Knowledge {name: $name, subject: $subject, grade: $grade}) 
            RETURN k
        """, name=data['name'], subject=data['subject'], grade=data['grade'])
        
        if existing.single():
            return jsonify({'error': 'Knowledge with same name, subject and grade already exists', 'success': False}), 409
        
        # Create knowledge
        knowledge_data = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'description': data.get('description', f"Kiến thức về: {data['name']}"),
            'order': data.get('order', 1),
            'subject': data['subject'],
            'grade': data['grade'],
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        result = session.run("""
            CREATE (k:Knowledge {
                id: $id, name: $name, description: $description, order: $order,
                subject: $subject, grade: $grade, 
                createdAt: $createdAt, updatedAt: $updatedAt
            })
            RETURN k
        """, knowledge_data)
        
        created_knowledge = dict(result.single()["k"].items())
    
    return jsonify({
        'message': 'Knowledge created successfully', 
        'knowledge': created_knowledge, 
        'success': True
    }), 201

@app.route('/api/v1/users/<user_id>/knowledge/<knowledge_id>', methods=['POST'])
@handle_errors
def link_user_knowledge(user_id, knowledge_id):
    """Link user to knowledge with timestamp"""
    with neo4j_api.driver.session() as session:
        # Check if user exists
        user_check = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
        if not user_check.single():
            return jsonify({'error': 'User not found', 'success': False}), 404
        
        # Check if knowledge exists  
        knowledge_check = session.run("MATCH (k:Knowledge {id: $knowledge_id}) RETURN k", knowledge_id=knowledge_id)
        knowledge_record = knowledge_check.single()
        if not knowledge_record:
            return jsonify({'error': 'Knowledge not found', 'success': False}), 404
        
        knowledge = dict(knowledge_record["k"].items())
        
        # Check if relationship already exists
        existing_rel = session.run("""
            MATCH (u:User {id: $user_id})-[r:LEARNED]->(k:Knowledge {id: $knowledge_id})
            RETURN r
        """, user_id=user_id, knowledge_id=knowledge_id)
        
        if existing_rel.single():
            return jsonify({'error': 'User already linked to this knowledge', 'success': False}), 409
        
        # Create relationship with timestamp
        now = datetime.now().isoformat()
        result = session.run("""
            MATCH (u:User {id: $user_id})
            MATCH (k:Knowledge {id: $knowledge_id})
            CREATE (u)-[r:LEARNED {
                linkedAt: $linkedAt,
                status: 'learning',
                progress: 0,
                createdAt: $linkedAt,
                updatedAt: $linkedAt
            }]->(k)
            RETURN u.name as user_name, k.name as knowledge_name, r
        """, user_id=user_id, knowledge_id=knowledge_id, linkedAt=now)
        
        link_result = result.single()
        relationship = dict(link_result["r"].items())
    
    return jsonify({
        'message': f'User linked to knowledge successfully',
        'link': {
            'user_name': link_result['user_name'],
            'knowledge_name': link_result['knowledge_name'],
            'relationship': relationship,
            'knowledge_info': knowledge
        },
        'success': True
    }), 201

@app.route('/api/v1/users/<user_id>/knowledge', methods=['GET'])
@handle_errors
def get_user_knowledge(user_id):
    """Get all knowledge linked to a user"""
    with neo4j_api.driver.session() as session:
        # Check if user exists
        user_check = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
        user_record = user_check.single()
        if not user_record:
            return jsonify({'error': 'User not found', 'success': False}), 404
        
        user = dict(user_record["u"].items())
        
        # Get all knowledge linked to user
        result = session.run("""
            MATCH (u:User {id: $user_id})-[r:LEARNED]->(k:Knowledge)
            RETURN k, r, 
                   substring(r.linkedAt, 0, 10) as linked_date,
                   substring(r.linkedAt, 11, 8) as linked_time
            ORDER BY r.linkedAt DESC
        """, user_id=user_id)
        
        user_knowledge = []
        for record in result:
            knowledge = dict(record["k"].items())
            relationship = dict(record["r"].items())
            
            knowledge_link = {
                'knowledge': knowledge,
                'relationship': relationship,
                'linked_date': record['linked_date'],
                'linked_time': record['linked_time']
            }
            user_knowledge.append(knowledge_link)
    
    return jsonify({
        'user': user,
        'knowledge_list': user_knowledge,
        'total_knowledge': len(user_knowledge),
        'success': True
    })

@app.route('/api/v1/knowledge/<knowledge_id>/users', methods=['GET'])
@handle_errors
def get_knowledge_users(knowledge_id):
    """Get all users linked to a knowledge"""
    with neo4j_api.driver.session() as session:
        # Check if knowledge exists
        knowledge_check = session.run("MATCH (k:Knowledge {id: $knowledge_id}) RETURN k", knowledge_id=knowledge_id)
        knowledge_record = knowledge_check.single()
        if not knowledge_record:
            return jsonify({'error': 'Knowledge not found', 'success': False}), 404
        
        knowledge = dict(knowledge_record["k"].items())
        
        # Get all users linked to knowledge
        result = session.run("""
            MATCH (u:User)-[r:LEARNED]->(k:Knowledge {id: $knowledge_id})
            RETURN u, r,
                   substring(r.linkedAt, 0, 10) as linked_date,
                   substring(r.linkedAt, 11, 8) as linked_time
            ORDER BY r.linkedAt DESC
        """, knowledge_id=knowledge_id)
        
        knowledge_users = []
        for record in result:
            user = dict(record["u"].items())
            relationship = dict(record["r"].items())
            
            user_link = {
                'user': user,
                'relationship': relationship,
                'linked_date': record['linked_date'],
                'linked_time': record['linked_time']
            }
            knowledge_users.append(user_link)
    
    return jsonify({
        'knowledge': knowledge,
        'users_list': knowledge_users,
        'total_users': len(knowledge_users),
        'success': True
    })

@app.route('/api/v1/users/<user_id>/knowledge/<knowledge_id>', methods=['PUT'])
@handle_errors
@validate_json
def update_user_knowledge_progress(user_id, knowledge_id):
    """Update user's progress on specific knowledge"""
    data = request.get_json()
    
    with neo4j_api.driver.session() as session:
        # Check if relationship exists
        rel_check = session.run("""
            MATCH (u:User {id: $user_id})-[r:LEARNED]->(k:Knowledge {id: $knowledge_id})
            RETURN r, u.name as user_name, k.name as knowledge_name
        """, user_id=user_id, knowledge_id=knowledge_id)
        
        rel_record = rel_check.single()
        if not rel_record:
            return jsonify({'error': 'User-Knowledge relationship not found', 'success': False}), 404
        
        # Update relationship
        update_data = {
            'user_id': user_id,
            'knowledge_id': knowledge_id,
            'updatedAt': datetime.now().isoformat()
        }
        
        # Add optional updates
        if 'progress' in data:
            progress = min(100, max(0, int(data['progress'])))  # Clamp between 0-100
            update_data['progress'] = progress
        
        if 'status' in data:
            allowed_statuses = ['learning', 'completed', 'mastered', 'reviewing']
            if data['status'] in allowed_statuses:
                update_data['status'] = data['status']
        
        # Build update query
        set_clauses = ['r.updatedAt = $updatedAt']
        if 'progress' in update_data:
            set_clauses.append('r.progress = $progress')
        if 'status' in update_data:
            set_clauses.append('r.status = $status')
        
        query = f"""
        MATCH (u:User {{id: $user_id}})-[r:LEARNED]->(k:Knowledge {{id: $knowledge_id}})
        SET {', '.join(set_clauses)}
        RETURN r, u.name as user_name, k.name as knowledge_name
        """
        
        result = session.run(query, update_data)
        updated_record = result.single()
        updated_relationship = dict(updated_record["r"].items())
    
    return jsonify({
        'message': 'User knowledge progress updated',
        'update': {
            'user_name': updated_record['user_name'],
            'knowledge_name': updated_record['knowledge_name'],
            'relationship': updated_relationship
        },
        'success': True
    })

@app.route('/api/v1/users/<user_id>/knowledge/<knowledge_id>', methods=['DELETE'])
@handle_errors
def unlink_user_knowledge(user_id, knowledge_id):
    """Remove link between user and knowledge"""
    with neo4j_api.driver.session() as session:
        # Check if relationship exists and get info
        rel_check = session.run("""
            MATCH (u:User {id: $user_id})-[r:LEARNED]->(k:Knowledge {id: $knowledge_id})
            RETURN r, u.name as user_name, k.name as knowledge_name
        """, user_id=user_id, knowledge_id=knowledge_id)
        
        rel_record = rel_check.single()
        if not rel_record:
            return jsonify({'error': 'User-Knowledge relationship not found', 'success': False}), 404
        
        # Delete relationship
        session.run("""
            MATCH (u:User {id: $user_id})-[r:LEARNED]->(k:Knowledge {id: $knowledge_id})
            DELETE r
        """, user_id=user_id, knowledge_id=knowledge_id)
    
    return jsonify({
        'message': f'User unlinked from knowledge successfully',
        'unlinked': {
            'user_name': rel_record['user_name'],
            'knowledge_name': rel_record['knowledge_name']
        },
        'success': True
    })

@app.route('/api/v1/users/bulk/knowledge', methods=['POST'])
@handle_errors
@validate_json
def bulk_link_users_knowledge():
    """Bulk link multiple users to multiple knowledge"""
    data = request.get_json()
    
    if 'links' not in data:
        return jsonify({'error': 'links array required', 'success': False}), 400
    
    links_data = data['links']
    created_links = []
    errors = []
    
    with neo4j_api.driver.session() as session:
        with session.begin_transaction() as tx:
            try:
                # Validate and prepare links
                valid_links = []
                user_ids = set()
                knowledge_ids = set()
                
                for i, link in enumerate(links_data):
                    if not all(field in link for field in ['user_id', 'knowledge_id']):
                        errors.append(f'Link {i}: Missing user_id or knowledge_id')
                        continue
                    
                    link_data = {
                        'user_id': link['user_id'],
                        'knowledge_id': link['knowledge_id'],
                        'status': link.get('status', 'learning'),
                        'progress': min(100, max(0, link.get('progress', 0))),
                        'linkedAt': datetime.now().isoformat()
                    }
                    link_data['createdAt'] = link_data['linkedAt']
                    link_data['updatedAt'] = link_data['linkedAt']
                    
                    valid_links.append(link_data)
                    user_ids.add(link['user_id'])
                    knowledge_ids.add(link['knowledge_id'])
                
                if not valid_links:
                    return jsonify({'error': 'No valid links to create', 'errors': errors, 'success': False}), 400
                
                # Validate users and knowledge exist
                existing_users = set()
                existing_knowledge = set()
                
                if user_ids:
                    user_result = tx.run("MATCH (u:User) WHERE u.id IN $user_ids RETURN u.id as id", user_ids=list(user_ids))
                    existing_users = {record['id'] for record in user_result}
                
                if knowledge_ids:
                    knowledge_result = tx.run("MATCH (k:Knowledge) WHERE k.id IN $knowledge_ids RETURN k.id as id", knowledge_ids=list(knowledge_ids))
                    existing_knowledge = {record['id'] for record in knowledge_result}
                
                # Filter valid links
                final_links = []
                for link in valid_links:
                    if link['user_id'] not in existing_users:
                        errors.append(f'User {link["user_id"]} not found')
                        continue
                    if link['knowledge_id'] not in existing_knowledge:
                        errors.append(f'Knowledge {link["knowledge_id"]} not found')
                        continue
                    final_links.append(link)
                
                # Check for existing relationships
                if final_links:
                    existing_rels = set()
                    existing_result = tx.run("""
                        MATCH (u:User)-[r:LEARNED]->(k:Knowledge)
                        WHERE u.id IN $user_ids AND k.id IN $knowledge_ids
                        RETURN u.id + '|' + k.id as link_key
                    """, user_ids=list(user_ids), knowledge_ids=list(knowledge_ids))
                    existing_rels = {record['link_key'] for record in existing_result}
                    
                    # Filter out existing relationships
                    new_links = []
                    for link in final_links:
                        link_key = f"{link['user_id']}|{link['knowledge_id']}"
                        if link_key in existing_rels:
                            errors.append(f'User {link["user_id"]} already linked to knowledge {link["knowledge_id"]}')
                        else:
                            new_links.append(link)
                    
                    final_links = new_links
                
                # Bulk create relationships
                if final_links:
                    tx.run("""
                        UNWIND $links as link
                        MATCH (u:User {id: link.user_id})
                        MATCH (k:Knowledge {id: link.knowledge_id})
                        CREATE (u)-[r:LEARNED {
                            linkedAt: link.linkedAt,
                            status: link.status,
                            progress: link.progress,
                            createdAt: link.createdAt,
                            updatedAt: link.updatedAt
                        }]->(k)
                    """, links=final_links)
                    
                    created_links = final_links
                
                tx.commit()
                
            except Exception as e:
                tx.rollback()
                return jsonify({'error': f'Transaction failed: {str(e)}', 'success': False}), 500
    
    return jsonify({
        'message': f'{len(created_links)} user-knowledge links created successfully',
        'created_links': created_links,
        'total_processed': len(links_data),
        'total_created': len(created_links),
        'total_errors': len(errors),
        'errors': errors,
        'success': len(created_links) > 0
    }), 201

@app.route('/api/v1/users-knowledge/analytics', methods=['GET'])
@handle_errors
def get_user_knowledge_analytics():
    """Get analytics for user-knowledge relationships"""
    with neo4j_api.driver.session() as session:
        # Overall statistics
        overall_stats = session.run("""
            MATCH (u:User)-[r:LEARNED]->(k:Knowledge)
            RETURN count(DISTINCT u) as total_users_learning,
                   count(DISTINCT k) as total_knowledge_being_learned,
                   count(r) as total_relationships,
                   avg(r.progress) as avg_progress
        """)
        
        stats_record = overall_stats.single()
        overall = dict(stats_record) if stats_record else {}
        
        # Progress distribution
        progress_stats = session.run("""
            MATCH (u:User)-[r:LEARNED]->(k:Knowledge)
            WITH CASE 
                WHEN r.progress = 0 THEN 'Not Started'
                WHEN r.progress < 25 THEN 'Beginner (1-24%)'
                WHEN r.progress < 50 THEN 'Intermediate (25-49%)'
                WHEN r.progress < 75 THEN 'Advanced (50-74%)'
                WHEN r.progress < 100 THEN 'Near Complete (75-99%)'
                ELSE 'Completed (100%)'
            END as progress_range
            RETURN progress_range, count(*) as count
            ORDER BY count DESC
        """)
        
        progress_distribution = {record['progress_range']: record['count'] for record in progress_stats}
        
        # Status distribution
        status_stats = session.run("""
            MATCH (u:User)-[r:LEARNED]->(k:Knowledge)
            RETURN r.status as status, count(*) as count
            ORDER BY count DESC
        """)
        
        status_distribution = {record['status']: record['count'] for record in status_stats}
        
        # Most popular knowledge
        popular_knowledge = session.run("""
            MATCH (u:User)-[r:LEARNED]->(k:Knowledge)
            RETURN k.name as knowledge_name, k.subject as subject, k.grade as grade,
                   count(u) as learner_count,
                   avg(r.progress) as avg_progress
            ORDER BY learner_count DESC
            LIMIT 10
        """)
        
        popular_list = [dict(record) for record in popular_knowledge]
        
        # Most active users
        active_users = session.run("""
            MATCH (u:User)-[r:LEARNED]->(k:Knowledge)
            RETURN u.name as user_name, u.email as user_email,
                   count(k) as knowledge_count,
                   avg(r.progress) as avg_progress,
                   max(r.linkedAt) as latest_activity
            ORDER BY knowledge_count DESC
            LIMIT 10
        """)
        
        active_list = [dict(record) for record in active_users]
    
    return jsonify({
        'overall_stats': overall,
        'progress_distribution': progress_distribution,
        'status_distribution': status_distribution,
        'most_popular_knowledge': popular_list,
        'most_active_users': active_list,
        'success': True
    })
# ==================== DETAILED STUDENT ANALYTICS ====================

@app.route('/api/v1/students/<user_id>/detailed', methods=['GET'])
@handle_errors
def get_student_detailed_info(user_id):
    """Get detailed information for a single student - NOT statistics"""
    with neo4j_api.driver.session() as session:
        # Check user exists
        user_check = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
        user_record = user_check.single()
        if not user_record:
            return jsonify({'error': 'Student not found', 'success': False}), 404
        
        student = dict(user_record["u"].items())
        
        # Get detailed answers with full context
        detailed_answers = session.run("""
            MATCH (u:User {id: $user_id})-[:ANSWERED]->(a:Answer)-[:ANSWERS_QUESTION]->(q:Question)
            MATCH (q)-[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
            MATCH (c)-[:BELONGS_TO_TYPE_BOOK]->(t:TypeBook)-[:BELONGS_TO_SUBJECT]->(s:Subject)
            RETURN {
                answer_id: a.id,
                student_answer: a.student_answer,
                is_correct: a.is_correct,
                start_time: a.start_time,
                completion_time: a.completion_time,
                duration_seconds: a.duration_seconds,
                question: {
                    id: q.id,
                    title: q.title,
                    content: q.content,
                    correct_answer: q.correct_answer,
                    difficulty: q.difficulty,
                    page: q.page,
                    image_question: q.image_question,
                    image_answer: q.image_answer
                },
                lesson: {
                    id: l.id,
                    name: l.name,
                    order: l.order
                },
                chapter: {
                    id: c.id,
                    name: c.name,
                    order: c.order
                },
                typebook: {
                    id: t.id,
                    name: t.name
                },
                subject: {
                    id: s.id,
                    name: s.name
                }
            } as answer_detail
            ORDER BY a.completion_time DESC
        """, user_id=user_id)
        
        answers_list = [record['answer_detail'] for record in detailed_answers] if detailed_answers else []
        
        # Get learning progress by subject - FIX: separate queries to avoid nested collect()
        learning_progress = session.run("""
            MATCH (u:User {id: $user_id})-[:ANSWERED]->(a:Answer)-[:ANSWERS_QUESTION]->(q:Question)
            MATCH (q)-[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
            MATCH (c)-[:BELONGS_TO_TYPE_BOOK]->(t:TypeBook)-[:BELONGS_TO_SUBJECT]->(s:Subject)
            RETURN s.id as subject_id, s.name as subject_name,
                   collect(DISTINCT {id: t.id, name: t.name}) as typebooks,
                   collect(DISTINCT {id: c.id, name: c.name, order: c.order}) as chapters,
                   max(a.completion_time) as latest_activity,
                   min(a.start_time) as first_activity
            ORDER BY s.name
        """, user_id=user_id)
        
        progress_list = []
        for record in learning_progress:
            progress_item = {
                'subject': {
                    'id': record['subject_id'],
                    'name': record['subject_name']
                },
                'typebooks': record['typebooks'],
                'chapters': record['chapters'],
                'latest_activity': record['latest_activity'],
                'first_activity': record['first_activity']
            }
            progress_list.append(progress_item)
        
        # Get recent mistakes for learning improvement
        recent_mistakes = session.run("""
            MATCH (u:User {id: $user_id})-[:ANSWERED]->(a:Answer {is_correct: false})-[:ANSWERS_QUESTION]->(q:Question)
            MATCH (q)-[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
            RETURN {
                answer_id: a.id,
                student_answer: a.student_answer,
                completion_time: a.completion_time,
                question: {
                    id: q.id,
                    title: q.title,
                    content: q.content,
                    correct_answer: q.correct_answer,
                    difficulty: q.difficulty,
                    page: q.page
                },
                lesson_name: l.name,
                chapter_name: c.name
            } as mistake
            ORDER BY a.completion_time DESC
            LIMIT 10
        """, user_id=user_id)
        
        mistakes_list = [record['mistake'] for record in recent_mistakes] if recent_mistakes else []
        
        # Get current study streak - FIX: handle datetime format properly and check for None
        study_streak = session.run("""
            MATCH (u:User {id: $user_id})-[:ANSWERED]->(a:Answer)
            WHERE a.completion_time IS NOT NULL
            WITH DISTINCT substring(a.completion_time, 0, 10) as study_date
            ORDER BY study_date DESC
            RETURN collect(study_date) as study_dates
        """, user_id=user_id)
        
        study_streak_result = study_streak.single()
        study_dates = study_streak_result['study_dates'] if study_streak_result and study_streak_result['study_dates'] else []
    
    return jsonify({
        'student': student,
        'detailed_answers': answers_list,
        'learning_progress': progress_list,
        'recent_mistakes': mistakes_list,
        'study_dates': study_dates,
        'summary_counts': {
            'total_answers': len(answers_list),
            'correct_answers': len([a for a in answers_list if a.get('is_correct', False)]),
            'subjects_studied': len(progress_list),
            'recent_mistakes': len(mistakes_list)
        },
        'has_data': len(answers_list) > 0,
        'success': True
    })

@app.route('/api/v1/students/detailed', methods=['GET'])
@handle_errors
def get_multiple_students_detailed():
    """Get detailed information for multiple students"""
    # Get query parameters
    user_ids = request.args.get('user_ids', '').split(',') if request.args.get('user_ids') else []
    subject_id = request.args.get('subject_id')
    chapter_id = request.args.get('chapter_id')
    lesson_id = request.args.get('lesson_id')
    limit = int(request.args.get('limit', 20))
    
    with neo4j_api.driver.session() as session:
        # Build dynamic query based on parameters
        base_query = """
        MATCH (u:User)-[:ANSWERED]->(a:Answer)-[:ANSWERS_QUESTION]->(q:Question)
        MATCH (q)-[:BELONGS_TO_LESSON]->(l:Lesson)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
        MATCH (c)-[:BELONGS_TO_TYPE_BOOK]->(t:TypeBook)-[:BELONGS_TO_SUBJECT]->(s:Subject)
        """
        
        conditions = []
        params = {'limit': limit}
        
        if user_ids and user_ids != ['']:
            conditions.append("u.id IN $user_ids")
            params['user_ids'] = user_ids
        
        if subject_id:
            conditions.append("s.id = $subject_id")
            params['subject_id'] = subject_id
        
        if chapter_id:
            conditions.append("c.id = $chapter_id")
            params['chapter_id'] = chapter_id
        
        if lesson_id:
            conditions.append("l.id = $lesson_id")
            params['lesson_id'] = lesson_id
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        # Get detailed student information - FIX: avoid nested collections
        detailed_query = base_query + """
        WITH u, collect({
            answer_id: a.id,
            student_answer: a.student_answer,
            is_correct: a.is_correct,
            start_time: a.start_time,
            completion_time: a.completion_time,
            duration_seconds: a.duration_seconds,
            question: {
                id: q.id,
                title: q.title,
                content: q.content,
                correct_answer: q.correct_answer,
                difficulty: q.difficulty,
                page: q.page
            },
            hierarchy: {
                subject_name: s.name,
                typebook_name: t.name,
                chapter_name: c.name,
                lesson_name: l.name
            }
        }) as answers
        
        RETURN {
            student: {
                id: u.id,
                name: u.name,
                email: u.email,
                age: u.age,
                createdAt: u.createdAt
            },
            answers: answers
        } as student_data
        ORDER BY u.name
        LIMIT $limit
        """
        
        result = session.run(detailed_query, params)
        students_data = []
        
        for record in result:
            student_info = record['student_data']
            
            # Calculate additional metrics for each student
            answers = student_info['answers']
            correct_count = len([a for a in answers if a['is_correct']])
            total_count = len(answers)
            
            # Group answers by subject
            subjects_map = {}
            for answer in answers:
                subject_name = answer['hierarchy']['subject_name']
                if subject_name not in subjects_map:
                    subjects_map[subject_name] = []
                subjects_map[subject_name].append(answer)
            
            # Get recent activity
            recent_answers = sorted(answers, key=lambda x: x['completion_time'], reverse=True)[:5]
            
            # Get performance by difficulty
            difficulty_performance = {}
            for answer in answers:
                difficulty = answer['question']['difficulty']
                if difficulty not in difficulty_performance:
                    difficulty_performance[difficulty] = {'total': 0, 'correct': 0}
                difficulty_performance[difficulty]['total'] += 1
                if answer['is_correct']:
                    difficulty_performance[difficulty]['correct'] += 1
            
            student_detailed = {
                'student': student_info['student'],
                'all_answers': answers,
                'recent_answers': recent_answers,
                'subjects_studied': list(subjects_map.keys()),
                'answers_by_subject': subjects_map,
                'difficulty_performance': difficulty_performance,
                'metrics': {
                    'total_answers': total_count,
                    'correct_answers': correct_count,
                    'accuracy_rate': round(correct_count / total_count * 100, 2) if total_count > 0 else 0,
                    'avg_duration': round(sum(a['duration_seconds'] for a in answers) / len(answers), 0) if answers else 0,
                    'subjects_count': len(subjects_map)
                }
            }
            
            students_data.append(student_detailed)
        
        # Get filter information for response
        filter_info = {
            'applied_filters': {
                'user_ids': user_ids if user_ids != [''] else None,
                'subject_id': subject_id,
                'chapter_id': chapter_id,
                'lesson_id': lesson_id,
                'limit': limit
            },
            'total_students': len(students_data)
        }
    
    return jsonify({
        'students': students_data,
        'filter_info': filter_info,
        'success': True
    })
# ==================== API DOCUMENTATION ====================

@app.route('/', methods=['GET'])
def api_docs():
    """API documentation with correct structure"""
    docs = {
        'name': 'Education API - Correct Neo4j Structure',
        'version': 'v1',
        'hierarchy': 'Subject → TypeBook → Chapter → Lesson → Question',
        'relationships': {
            'User -[:ANSWERED]-> Answer': 'User answers questions',
            'Answer -[:ANSWERS_QUESTION]-> Question': 'Answer links to question',
            'Question -[:BELONGS_TO_LESSON]-> Lesson': 'Question belongs to lesson',
            'Lesson -[:BELONGS_TO_CHAPTER]-> Chapter': 'Lesson belongs to chapter',
            'Chapter -[:BELONGS_TO_TYPE_BOOK]-> TypeBook': 'Chapter belongs to typebook',
            'TypeBook -[:BELONGS_TO_SUBJECT]-> Subject': 'TypeBook belongs to subject'
        },
        'endpoints': {
            'Tree Structure': {
                'GET /api/v1/tree': 'Get complete tree with all IDs (?include_users=true&include_questions=true)',
                'GET /api/v1/tree/ids-only': 'Get minimal tree structure (only IDs)',
                'GET /api/v1/tree/flat': 'Get flattened structure for easy navigation'
            },
            'Hierarchy': {
                'GET /api/v1/subjects': 'Get all subjects',
                'GET /api/v1/typebooks': 'Get typebooks (?subject_id=xxx)',
                'GET /api/v1/chapters': 'Get chapters (?typebook_id=xxx)',
                'GET /api/v1/lessons': 'Get lessons (?chapter_id=xxx)'
            },
            'Users': {
                'GET /api/v1/users': 'Get all users',
                'POST /api/v1/users': 'Create user',
                'POST /api/v1/users/bulk': 'Import users'
            },
            'Questions': {
                'GET /api/v1/questions': 'Get questions (?lesson_id=xxx or ?chapter_id=xxx)',
                'POST /api/v1/questions': 'Create question (requires lesson_id)',
                'POST /api/v1/questions/bulk': 'Import questions'
            },
            'Answers': {
                'GET /api/v1/answers': 'Get answers (?user_id=xxx or ?question_id=xxx)',
                'POST /api/v1/answers': 'Submit answer',
                'POST /api/v1/answers/bulk': 'Import answers'
            },
            'Analytics': {
                'GET /api/v1/analytics/hierarchy': 'Analytics by hierarchy',
                'GET /api/v1/analytics/user/{user_id}': 'User performance analytics'
            },
            'Export': {
                'GET /api/v1/export': 'Export all data with hierarchy'
            }
        },
        'examples': {
            'create_question_correct': {
                'POST /api/v1/questions': {
                    'lesson_id': 'lesson-uuid-from-existing-lesson',
                    'title': 'bài 1 trang 7 sách giáo khoa toán lớp 1',
                    'content': 'Dùng các từ: trên, dưới, trái, phải để nói về bức tranh?',
                    'correct_answer': 'Bạn Lan đang ngồi ở giữa bàn học...',
                    'difficulty': 'dễ',
                    'page': 7,
                    'image_question': 'images/bai1-trang7-sgk.png'
                }
            },
            'submit_answer_correct': {
                'POST /api/v1/answers': {
                    'user_id': 'user-uuid',
                    'question_id': 'question-uuid',
                    'student_answer': 'Em thấy có 3 quả táo',
                    'is_correct': True,
                    'duration_seconds': 120
                }
            },
            'import_questions_bulk': {
                'POST /api/v1/questions/bulk': {
                    'questions': [
                        {
                            'lesson_id': 'lesson-uuid',
                            'title': 'Câu hỏi 1',
                            'content': 'Nội dung câu hỏi 1',
                            'correct_answer': 'Đáp án đúng',
                            'difficulty': 'dễ',
                            'page': 7
                        }
                    ]
                }
            }
        },
        'workflow': {
            '1': 'Tạo/Lấy Subject → TypeBook → Chapter → Lesson (hierarchy có sẵn)',
            '2': 'Tạo Question với lesson_id → tự động link đến Lesson',
            '3': 'User trả lời → tạo Answer với user_id + question_id → tự động link relationships',
            '4': 'Query có thể trace được full hierarchy: Subject → TypeBook → Chapter → Lesson → Question → Answer → User'
        },
        'note': 'Mọi Question phải có lesson_id. Mọi Answer phải có user_id + question_id. Relationships sẽ tự động được tạo.'
    }
    
    return jsonify(docs)

# ==================== STARTUP ====================

if __name__ == '__main__':
    try:
        logger.info("🚀 Starting Education API with Correct Neo4j Structure...")
        logger.info("📊 Documentation: http://localhost:5000/")
        logger.info("💊 Health: http://localhost:5000/api/v1/health")
        logger.info("📋 Hierarchy: Subject → TypeBook → Chapter → Lesson → Question")
        
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('DEBUG', 'False').lower() == 'true'
        )
    except KeyboardInterrupt:
        logger.info("🛑 API shutdown")
    except Exception as e:
        logger.error(f"💥 Startup failed: {e}")
    finally:
        neo4j_api.close()