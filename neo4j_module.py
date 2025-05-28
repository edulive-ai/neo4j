#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Education System Class for Internal Use
Direct Neo4j operations without API
Includes: User Management, Test System, Knowledge Management, Analytics
"""

import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from neo4j import GraphDatabase
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EducationSystem:
    """
    Complete Education System for managing users, tests, knowledge directly with Neo4j
    No API required - for internal use only
    
    Features:
    - User Management (CRUD, bulk operations)
    - Test System (create tests, questions, answers)
    - Knowledge Management (link users to knowledge)
    - Analytics and Statistics
    - Hierarchy Management (subjects, chapters, lessons)
    """
    
    def __init__(self, 
                 uri: str = None, 
                 username: str = None, 
                 password: str = None):
        """
        Initialize Education System with Neo4j connection
        
        Args:
            uri: Neo4j connection URI (default from env)
            username: Neo4j username (default from env)
            password: Neo4j password (default from env)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "neo4j://14.232.211.211:17687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "OPGk80GA26Q4")
        self.driver = None
        self.connect()
    
    def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("✅ Connected to Neo4j successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("🔌 Neo4j connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return {'status': 'healthy', 'success': True}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e), 'success': False}

    # ==================== USER MANAGEMENT ====================
    
    def create_user(self, name: str, email: str, age: int = 7, user_id: str = None) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            name: User's name
            email: User's email (must be unique)
            age: User's age (default: 7)
            user_id: Custom user ID (optional, auto-generate if not provided)
            
        Returns:
            Dictionary containing user information or error
        """
        with self.driver.session() as session:
            # Check if email exists
            existing_email = session.run("MATCH (u:User {email: $email}) RETURN u", email=email.strip().lower())
            if existing_email.single():
                return {'error': 'Email already exists', 'success': False}
            
            # If user_id is provided, check if it already exists
            if user_id:
                existing_id = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
                if existing_id.single():
                    return {'error': 'User ID already exists', 'success': False}
            
            # Create user
            user_data = {
                'id': user_id or str(uuid.uuid4()),
                'name': name.strip(),
                'email': email.strip().lower(),
                'age': age,
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
            return {'message': 'User created successfully', 'user': created_user, 'success': True}
    
    def get_users(self) -> Dict[str, Any]:
        """Get all users"""
        with self.driver.session() as session:
            result = session.run("MATCH (u:User) RETURN u ORDER BY u.name")
            users = [dict(record["u"].items()) for record in result]
        return {'users': users, 'count': len(users), 'success': True}
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID"""
        with self.driver.session() as session:
            result = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
            user_record = result.single()
            if not user_record:
                return {'error': 'User not found', 'success': False}
            return {'user': dict(user_record["u"].items()), 'success': True}
    
    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email"""
        with self.driver.session() as session:
            result = session.run("MATCH (u:User {email: $email}) RETURN u", email=email.lower())
            user_record = result.single()
            if not user_record:
                return {'error': 'User not found', 'success': False}
            return {'user': dict(user_record["u"].items()), 'success': True}

    def bulk_create_users(self, users_data: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        """
        Bulk create users with validation and error handling
        
        Args:
            users_data: List of user dictionaries with name, email, age, and optional id
            batch_size: Number of users to process in each batch
            
        Returns:
            Dictionary with created users, errors, and statistics
        """
        created_users = []
        errors = []
        used_ids = set()  # Track IDs to prevent duplicates within the batch
        
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    # Validate all users first
                    valid_users = []
                    for i, user in enumerate(users_data):
                        # Check required fields
                        if not all(field in user for field in ['name', 'email']):
                            errors.append(f'User {i}: Missing name or email')
                            continue
                        
                        # Validate email format
                        if '@' not in user['email']:
                            errors.append(f'User {i}: Invalid email format')
                            continue
                        
                        # Handle ID assignment
                        user_id = user.get('id')
                        if user_id:
                            # Validate custom ID format (optional - adjust as needed)
                            user_id = str(user_id).strip()
                            if not user_id:
                                errors.append(f'User {i}: Empty ID provided')
                                continue
                            
                            # Check for duplicate IDs within the batch
                            if user_id in used_ids:
                                errors.append(f'User {i}: Duplicate ID "{user_id}" in batch')
                                continue
                            used_ids.add(user_id)
                        else:
                            # Generate UUID if no ID provided
                            user_id = str(uuid.uuid4())
                        
                        user_data = {
                            'id': user_id,
                            'name': user['name'].strip(),
                            'email': user['email'].strip().lower(),
                            'age': user.get('age', 7),
                            'createdAt': datetime.now().isoformat(),
                            'updatedAt': datetime.now().isoformat()
                        }
                        valid_users.append(user_data)
                    
                    if not valid_users:
                        return {'error': 'No valid users to import', 'errors': errors, 'success': False}
                    
                    # Check for existing emails AND IDs in database
                    email_list = [user['email'] for user in valid_users]
                    id_list = [user['id'] for user in valid_users]
                    
                    # Check existing emails
                    existing_emails_result = tx.run("""
                        MATCH (u:User) 
                        WHERE u.email IN $email_list 
                        RETURN u.email as email
                    """, email_list=email_list)
                    existing_emails = [record['email'] for record in existing_emails_result]
                    
                    # Check existing IDs
                    existing_ids_result = tx.run("""
                        MATCH (u:User) 
                        WHERE u.id IN $id_list 
                        RETURN u.id as id
                    """, id_list=id_list)
                    existing_ids = [record['id'] for record in existing_ids_result]
                    
                    # Filter out existing emails and IDs
                    new_users = []
                    for user in valid_users:
                        skip_user = False
                        
                        if user['email'] in existing_emails:
                            errors.append(f'Email {user["email"]} already exists')
                            skip_user = True
                        
                        if user['id'] in existing_ids:
                            errors.append(f'ID {user["id"]} already exists')
                            skip_user = True
                        
                        if not skip_user:
                            new_users.append(user)
                    
                    # Bulk create users in batches
                    for i in range(0, len(new_users), batch_size):
                        batch = new_users[i:i + batch_size]
                        
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
                    return {'error': f'Transaction failed: {str(e)}', 'success': False}
        
        return {
            'message': f'{len(created_users)} users imported successfully',
            'created_users': created_users,
            'total_processed': len(users_data),
            'total_created': len(created_users),
            'total_errors': len(errors),
            'errors': errors,
            'success': len(created_users) > 0
        }

    # ==================== TEST SYSTEM ====================
    
    def create_complete_test(self, 
                           title: str, 
                           description: str, 
                           user_id: str, 
                           questions: List[Dict[str, Any]], 
                           duration_minutes: int = 60,
                           start_time: str = None) -> Dict[str, Any]:
        """
        Create a complete test with questions and answers in one operation
        
        Args:
            title: Test title
            description: Test description
            user_id: ID of the user taking the test
            questions: List of question dictionaries
            duration_minutes: Test duration (default: 60)
            start_time: Test start time (default: now)
            
        Returns:
            Dictionary with test, questions, answers, and summary
        """
        if not questions or len(questions) == 0:
            return {'error': 'Questions array cannot be empty', 'success': False}
        
        # Validate questions structure
        for i, q in enumerate(questions):
            required_fields = ['question', 'answer', 'student_answer', 'is_correct']
            if not all(field in q for field in required_fields):
                return {'error': f'Question {i}: Missing {required_fields}', 'success': False}
        
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    # Check if user exists
                    user_check = tx.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
                    user_record = user_check.single()
                    if not user_record:
                        return {'error': 'User not found', 'success': False}
                    
                    user_info = dict(user_record["u"].items())
                    
                    # Create Test
                    test_id = str(uuid.uuid4())
                    now = datetime.now().isoformat()
                    
                    test_data = {
                        'id': test_id,
                        'title': title,
                        'description': description,
                        'user_id': user_id,
                        'duration_minutes': duration_minutes,
                        'status': 'completed',
                        'start_time': start_time or now,
                        'end_time': now,
                        'createdAt': now,
                        'updatedAt': now
                    }
                    
                    tx.run("""
                        CREATE (t:Test {
                            id: $id, title: $title, description: $description, 
                            user_id: $user_id, duration_minutes: $duration_minutes, status: $status,
                            start_time: $start_time, end_time: $end_time,
                            createdAt: $createdAt, updatedAt: $updatedAt
                        })
                    """, test_data)
                    
                    # Create User-[:TOOK]->Test relationship
                    tx.run("""
                        MATCH (u:User {id: $user_id})
                        MATCH (t:Test {id: $test_id})
                        CREATE (u)-[:TOOK]->(t)
                    """, user_id=user_id, test_id=test_id)
                    
                    # Create Questions and TestAnswers
                    created_questions = []
                    created_answers = []
                    total_score = 0
                    max_possible_score = 0
                    
                    for i, question_data in enumerate(questions):
                        # Create Question
                        question_id = str(uuid.uuid4())
                        question_db_data = {
                            'id': question_id,
                            'content': question_data['question'],
                            'correct_answer': question_data['answer'],
                            'image_question': question_data.get('image_question', ''),
                            'image_answer': question_data.get('image_answer', ''),
                            'difficulty': question_data.get('difficulty', 'medium'),
                            'order': i + 1,
                            'createdAt': now,
                            'updatedAt': now
                        }
                        
                        tx.run("""
                            CREATE (q:Question {
                                id: $id, content: $content, correct_answer: $correct_answer,
                                image_question: $image_question, image_answer: $image_answer,
                                difficulty: $difficulty, order: $order, 
                                createdAt: $createdAt, updatedAt: $updatedAt
                            })
                        """, question_db_data)
                        
                        # Create Test-[:CONTAINS_QUESTION]->Question relationship
                        points = question_data.get('points', 1)
                        tx.run("""
                            MATCH (t:Test {id: $test_id})
                            MATCH (q:Question {id: $question_id})
                            CREATE (t)-[:CONTAINS_QUESTION {
                                order: $order,
                                points: $points,
                                addedAt: $addedAt
                            }]->(q)
                        """, test_id=test_id, question_id=question_id, order=i + 1, points=points, addedAt=now)
                        
                        created_questions.append(question_db_data)
                        
                        # Create TestAnswer
                        answer_id = str(uuid.uuid4())
                        max_possible_score += points
                        
                        answer_data = {
                            'id': answer_id,
                            'student_answer': question_data['student_answer'],
                            'is_correct': question_data['is_correct'],
                            'answered_at': now,
                            'duration_seconds': question_data.get('duration_seconds', 0),
                            'createdAt': now,
                            'updatedAt': now
                        }
                        
                        if question_data['is_correct']:
                            total_score += points
                        
                        tx.run("""
                            CREATE (ta:TestAnswer {
                                id: $id, student_answer: $student_answer, is_correct: $is_correct,
                                answered_at: $answered_at, duration_seconds: $duration_seconds,
                                createdAt: $createdAt, updatedAt: $updatedAt
                            })
                        """, answer_data)
                        
                        # Create Question-[:HAS_ANSWER]->TestAnswer relationship
                        tx.run("""
                            MATCH (q:Question {id: $question_id})
                            MATCH (ta:TestAnswer {id: $answer_id})
                            CREATE (q)-[:HAS_ANSWER {
                                points: $points,
                                answeredAt: $answeredAt
                            }]->(ta)
                        """, question_id=question_id, answer_id=answer_id, points=points, answeredAt=now)
                        
                        answer_data['question_info'] = question_db_data
                        answer_data['points'] = points
                        created_answers.append(answer_data)
                    
                    # Update test with scores
                    tx.run("""
                        MATCH (t:Test {id: $test_id})
                        SET t.total_score = $total_score,
                            t.max_possible_score = $max_possible_score,
                            t.total_questions = $total_questions,
                            t.correct_answers = $correct_answers,
                            t.accuracy_percentage = $accuracy_percentage,
                            t.updatedAt = $updatedAt
                    """, 
                    test_id=test_id,
                    total_score=total_score,
                    max_possible_score=max_possible_score,
                    total_questions=len(questions),
                    correct_answers=len([q for q in questions if q['is_correct']]),
                    accuracy_percentage=round(total_score / max_possible_score * 100, 2) if max_possible_score > 0 else 0,
                    updatedAt=now)
                    
                    tx.commit()
                    
                    return {
                        'message': 'Test created successfully',
                        'test': test_data,
                        'questions': created_questions,
                        'answers': created_answers,
                        'user': user_info,
                        'summary': {
                            'total_questions': len(questions),
                            'correct_answers': len([q for q in questions if q['is_correct']]),
                            'total_score': f"{total_score}/{max_possible_score}",
                            'accuracy_percentage': round(total_score / max_possible_score * 100, 2) if max_possible_score > 0 else 0,
                            'completion_time': now
                        },
                        'success': True
                    }
                    
                except Exception as e:
                    tx.rollback()
                    return {'error': f'Transaction failed: {str(e)}', 'success': False}

    def get_user_test_history(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete test history for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user info, test history, and summary
        """
        with self.driver.session() as session:
            # Check if user exists
            user_check = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
            user_record = user_check.single()
            if not user_record:
                return {'error': 'User not found', 'success': False}
            
            user_info = dict(user_record["u"].items())
            
            # Get all tests for user
            tests_result = session.run("""
                MATCH (u:User {id: $user_id})-[:TOOK]->(t:Test)
                RETURN t
                ORDER BY t.createdAt DESC
            """, user_id=user_id)
            
            test_history = []
            
            for test_record in tests_result:
                test = dict(test_record["t"].items())
                
                # Get questions and answers for this test
                qa_result = session.run("""
                    MATCH (t:Test {id: $test_id})-[:CONTAINS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(a:TestAnswer)
                    RETURN q, a
                    ORDER BY q.order
                """, test_id=test['id'])
                
                questions_and_answers = []
                correct_count = 0
                total_questions = 0
                
                for qa_record in qa_result:
                    question = dict(qa_record["q"].items())
                    answer = dict(qa_record["a"].items())
                    
                    qa_item = {
                        'question': {
                            'id': question['id'],
                            'content': question['content'],
                            'correct_answer': question['correct_answer'],
                            'image_question': question.get('image_question', ''),
                            'image_answer': question.get('image_answer', ''),
                            'difficulty': question.get('difficulty', 'medium')
                        },
                        'answer': {
                            'id': answer['id'],
                            'student_answer': answer['student_answer'],
                            'is_correct': answer['is_correct'],
                            'answered_at': answer['answered_at'],
                            'duration_seconds': answer['duration_seconds']
                        }
                    }
                    
                    questions_and_answers.append(qa_item)
                    total_questions += 1
                    if answer['is_correct']:
                        correct_count += 1
                
                test_item = {
                    'test': {
                        'id': test['id'],
                        'title': test['title'],
                        'description': test['description'],
                        'start_time': test.get('start_time'),
                        'end_time': test.get('end_time'),
                        'status': test.get('status', 'completed'),
                        'created_at': test['createdAt']
                    },
                    'questions_and_answers': questions_and_answers,
                    'summary': {
                        'total_questions': total_questions,
                        'correct_answers': correct_count,
                        'wrong_answers': total_questions - correct_count,
                        'accuracy_percentage': round(correct_count / total_questions * 100, 1) if total_questions > 0 else 0
                    }
                }
                
                test_history.append(test_item)
            
            return {
                'user': {
                    'id': user_info['id'],
                    'name': user_info['name'],
                    'email': user_info['email']
                },
                'test_history': test_history,
                'total_tests': len(test_history),
                'success': True
            }

    def get_test_details(self, test_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific test
        
        Args:
            test_id: Test ID
            
        Returns:
            Dictionary with test details, user info, questions, answers, and analysis
        """
        with self.driver.session() as session:
            # Get test and user info
            test_result = session.run("""
                MATCH (u:User)-[:TOOK]->(t:Test {id: $test_id})
                RETURN t, u
            """, test_id=test_id)
            
            test_record = test_result.single()
            if not test_record:
                return {'error': 'Test not found', 'success': False}
            
            test = dict(test_record["t"].items())
            user = dict(test_record["u"].items())
            
            # Get all questions and answers
            answers_result = session.run("""
                MATCH (u:User)-[:TOOK]->(t:Test {id: $test_id})-[:CONTAINS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(ta:TestAnswer)
                RETURN ta, q
                ORDER BY q.order
            """, test_id=test_id)
            
            detailed_answers = []
            for record in answers_result:
                answer = dict(record["ta"].items())
                question = dict(record["q"].items())
                
                answer_detail = {
                    'question': {
                        'id': question['id'],
                        'content': question['content'],
                        'correct_answer': question['correct_answer'],
                        'image_question': question.get('image_question', ''),
                        'image_answer': question.get('image_answer', ''),
                        'difficulty': question.get('difficulty', 'medium'),
                        'order': question['order']
                    },
                    'answer': {
                        'id': answer['id'],
                        'student_answer': answer['student_answer'],
                        'is_correct': answer['is_correct'],
                        'answered_at': answer['answered_at'],
                        'duration_seconds': answer['duration_seconds']
                    }
                }
                detailed_answers.append(answer_detail)
            
            # Calculate statistics
            total_questions = len(detailed_answers)
            correct_answers = len([a for a in detailed_answers if a['answer']['is_correct']])
            wrong_answers = total_questions - correct_answers
            
            # Difficulty analysis
            difficulty_analysis = {}
            for answer_detail in detailed_answers:
                difficulty = answer_detail['question'].get('difficulty', 'medium')
                if difficulty not in difficulty_analysis:
                    difficulty_analysis[difficulty] = {'total': 0, 'correct': 0, 'wrong': 0}
                difficulty_analysis[difficulty]['total'] += 1
                if answer_detail['answer']['is_correct']:
                    difficulty_analysis[difficulty]['correct'] += 1
                else:
                    difficulty_analysis[difficulty]['wrong'] += 1
            
            # Add accuracy rates
            for difficulty in difficulty_analysis:
                analysis = difficulty_analysis[difficulty]
                analysis['accuracy_rate'] = round(analysis['correct'] / analysis['total'] * 100, 2)
            
            return {
                'test': {
                    'id': test['id'],
                    'title': test['title'],
                    'description': test['description'],
                    'start_time': test.get('start_time'),
                    'end_time': test.get('end_time'),
                    'status': test.get('status', 'completed'),
                    'created_at': test['createdAt']
                },
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email']
                },
                'questions_and_answers': detailed_answers,
                'summary': {
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'wrong_answers': wrong_answers,
                    'accuracy_rate': round(correct_answers / total_questions * 100, 2) if total_questions > 0 else 0,
                    'total_time_spent': sum(a['answer']['duration_seconds'] for a in detailed_answers),
                    'avg_time_per_question': round(sum(a['answer']['duration_seconds'] for a in detailed_answers) / len(detailed_answers), 2) if detailed_answers else 0
                },
                'difficulty_analysis': difficulty_analysis,
                'success': True
            }

    def search_tests(self, 
                    user_id: str = None, 
                    title_search: str = None, 
                    from_date: str = None, 
                    to_date: str = None, 
                    min_score: float = None, 
                    max_score: float = None) -> Dict[str, Any]:
        """
        Search tests with various criteria
        
        Args:
            user_id: Filter by specific user
            title_search: Search in test titles
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            min_score: Minimum accuracy percentage
            max_score: Maximum accuracy percentage
            
        Returns:
            Dictionary with matching tests and search criteria
        """
        with self.driver.session() as session:
            query = "MATCH (u:User)-[:TOOK]->(t:Test)"
            conditions = []
            params = {}
            
            if user_id:
                conditions.append("u.id = $user_id")
                params['user_id'] = user_id
            
            if title_search:
                conditions.append("toLower(t.title) CONTAINS toLower($title_search)")
                params['title_search'] = title_search
            
            if from_date:
                conditions.append("t.createdAt >= $from_date")
                params['from_date'] = from_date
            
            if to_date:
                conditions.append("t.createdAt <= $to_date")
                params['to_date'] = to_date
            
            if min_score is not None:
                conditions.append("t.accuracy_percentage >= $min_score")
                params['min_score'] = min_score
            
            if max_score is not None:
                conditions.append("t.accuracy_percentage <= $max_score")
                params['max_score'] = max_score
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += """
            RETURN t, u.name as user_name, u.email as user_email,
                   t.total_questions as total_questions,
                   t.correct_answers as correct_answers,
                   t.accuracy_percentage as accuracy_percentage
            ORDER BY t.createdAt DESC
            """
            
            result = session.run(query, params)
            
            tests = []
            for record in result:
                test = dict(record["t"].items())
                test['user_name'] = record['user_name']
                test['user_email'] = record['user_email']
                tests.append(test)
            
            return {
                'tests': tests,
                'count': len(tests),
                'search_criteria': {
                    'user_id': user_id,
                    'title_search': title_search,
                    'from_date': from_date,
                    'to_date': to_date,
                    'min_score': min_score,
                    'max_score': max_score
                },
                'success': True
            }
    # ==================== ANALYTICS ====================
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user statistics and analytics
        """
        with self.driver.session() as session:
            # Check if user exists
            user_check = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
            user_record = user_check.single()
            if not user_record:
                return {'error': 'User not found', 'success': False}
            
            user_info = dict(user_record["u"].items())
            
            # Overall test statistics
            overall_stats = session.run("""
                MATCH (u:User {id: $user_id})-[:TOOK]->(t:Test)-[:CONTAINS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(a:TestAnswer)
                RETURN count(DISTINCT t) as total_tests,
                       count(q) as total_questions_answered,
                       count(CASE WHEN a.is_correct THEN 1 END) as correct_answers,
                       round(count(CASE WHEN a.is_correct THEN 1 END) * 100.0 / count(q), 2) as overall_accuracy,
                       avg(a.duration_seconds) as avg_time_per_question,
                       sum(a.duration_seconds) as total_study_time
            """, user_id=user_id)
            
            stats_record = overall_stats.single()
            overall = dict(stats_record) if stats_record else {}
            
            # Performance by difficulty
            difficulty_stats = session.run("""
                MATCH (u:User {id: $user_id})-[:TOOK]->(t:Test)-[:CONTAINS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(a:TestAnswer)
                RETURN q.difficulty as difficulty_level,
                       count(q) as total_questions,
                       count(CASE WHEN a.is_correct THEN 1 END) as correct_answers,
                       round(count(CASE WHEN a.is_correct THEN 1 END) * 100.0 / count(q), 2) as accuracy_rate
                ORDER BY difficulty_level
            """, user_id=user_id)
            
            difficulty_performance = [dict(record) for record in difficulty_stats]
            
            return {
                'user': user_info,
                'overall_statistics': overall,
                'difficulty_performance': difficulty_performance,
                'success': True
            }

    def get_system_analytics(self) -> Dict[str, Any]:
        """
        Get system-wide analytics and statistics
        
        Returns:
            Dictionary with comprehensive system statistics
        """
        with self.driver.session() as session:
            # Overall system stats
            system_stats = session.run("""
                MATCH (u:User) 
                OPTIONAL MATCH (u)-[:TOOK]->(t:Test)
                OPTIONAL MATCH (t)-[:CONTAINS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(a:TestAnswer)
                RETURN count(DISTINCT u) as total_users,
                       count(DISTINCT t) as total_tests,
                       count(DISTINCT q) as total_questions,
                       count(a) as total_answers,
                       count(CASE WHEN a.is_correct THEN 1 END) as total_correct_answers,
                       round(count(CASE WHEN a.is_correct THEN 1 END) * 100.0 / count(a), 2) as system_accuracy
            """)
            
            stats_record = system_stats.single()
            overall = dict(stats_record) if stats_record else {}
            
            # Most active users
            active_users = session.run("""
                MATCH (u:User)-[:TOOK]->(t:Test)
                RETURN u.name as user_name, u.email as user_email,
                       count(t) as tests_taken,
                       max(t.createdAt) as latest_activity
                ORDER BY tests_taken DESC
                LIMIT 10
            """)
            
            top_users = [dict(record) for record in active_users]
            
            # Test performance distribution
            performance_dist = session.run("""
                MATCH (t:Test)
                WHERE t.accuracy_percentage IS NOT NULL
                WITH CASE 
                    WHEN t.accuracy_percentage >= 90 THEN 'Excellent (90-100%)'
                    WHEN t.accuracy_percentage >= 80 THEN 'Good (80-89%)'
                    WHEN t.accuracy_percentage >= 70 THEN 'Average (70-79%)'
                    WHEN t.accuracy_percentage >= 60 THEN 'Below Average (60-69%)'
                    ELSE 'Poor (<60%)'
                END as performance_range
                RETURN performance_range, count(*) as count
                ORDER BY count DESC
            """)
            
            performance_distribution = {record['performance_range']: record['count'] for record in performance_dist}
            
            return {
                'overall_statistics': overall,
                'top_active_users': top_users,
                'performance_distribution': performance_distribution,
                'success': True
            }

    # ==================== KNOWLEDGE MANAGEMENT ====================
    
    def create_knowledge(self, name: str, subject: str, grade: str, description: str = None, order: int = 1) -> Dict[str, Any]:
        """
        Create new knowledge item
        
        Args:
            name: Knowledge name
            subject: Subject name
            grade: Grade level
            description: Optional description
            order: Sort order
            
        Returns:
            Dictionary with created knowledge or error
        """
        with self.driver.session() as session:
            # Check if knowledge already exists
            existing = session.run("""
                MATCH (k:Knowledge {name: $name, subject: $subject, grade: $grade}) 
                RETURN k
            """, name=name, subject=subject, grade=grade)
            
            if existing.single():
                return {'error': 'Knowledge with same name, subject and grade already exists', 'success': False}
            
            # Create knowledge
            knowledge_data = {
                'id': str(uuid.uuid4()),
                'name': name,
                'description': description or f"Kiến thức về: {name}",
                'order': order,
                'subject': subject,
                'grade': grade,
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
            return {'message': 'Knowledge created successfully', 'knowledge': created_knowledge, 'success': True}

    def get_knowledge(self, subject: str = None, grade: str = None) -> Dict[str, Any]:
        """
        Get knowledge items with optional filters
        
        Args:
            subject: Filter by subject
            grade: Filter by grade
            
        Returns:
            Dictionary with knowledge list
        """
        with self.driver.session() as session:
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
            
            return {
                'knowledge': knowledge_list, 
                'count': len(knowledge_list), 
                'filters': {'subject': subject, 'grade': grade},
                'success': True
            }

    def link_user_knowledge(self, user_id: str, knowledge_id: str, status: str = 'learning', progress: int = 0) -> Dict[str, Any]:
        """
        Link user to knowledge with progress tracking
        
        Args:
            user_id: User ID
            knowledge_id: Knowledge ID
            status: Learning status
            progress: Progress percentage (0-100)
            
        Returns:
            Dictionary with link info or error
        """
        with self.driver.session() as session:
            # Check if user and knowledge exist
            user_check = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
            if not user_check.single():
                return {'error': 'User not found', 'success': False}
            
            knowledge_check = session.run("MATCH (k:Knowledge {id: $knowledge_id}) RETURN k", knowledge_id=knowledge_id)
            knowledge_record = knowledge_check.single()
            if not knowledge_record:
                return {'error': 'Knowledge not found', 'success': False}
            
            knowledge = dict(knowledge_record["k"].items())
            
            # Check if relationship already exists
            existing_rel = session.run("""
                MATCH (u:User {id: $user_id})-[r:LEARNED]->(k:Knowledge {id: $knowledge_id})
                RETURN r
            """, user_id=user_id, knowledge_id=knowledge_id)
            
            if existing_rel.single():
                return {'error': 'User already linked to this knowledge', 'success': False}
            
            # Create relationship
            now = datetime.now().isoformat()
            result = session.run("""
                MATCH (u:User {id: $user_id})
                MATCH (k:Knowledge {id: $knowledge_id})
                CREATE (u)-[r:LEARNED {
                    linkedAt: $linkedAt,
                    status: $status,
                    progress: $progress,
                    createdAt: $linkedAt,
                    updatedAt: $linkedAt
                }]->(k)
                RETURN u.name as user_name, k.name as knowledge_name, r
            """, user_id=user_id, knowledge_id=knowledge_id, linkedAt=now, status=status, progress=min(100, max(0, progress)))
            
            link_result = result.single()
            relationship = dict(link_result["r"].items())
            
            return {
                'message': 'User linked to knowledge successfully',
                'link': {
                    'user_name': link_result['user_name'],
                    'knowledge_name': link_result['knowledge_name'],
                    'relationship': relationship,
                    'knowledge_info': knowledge
                },
                'success': True
            }

    def get_user_knowledge(self, user_id: str) -> Dict[str, Any]:
        """
        Get all knowledge linked to a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user's knowledge list
        """
        with self.driver.session() as session:
            # Check if user exists
            user_check = session.run("MATCH (u:User {id: $user_id}) RETURN u", user_id=user_id)
            user_record = user_check.single()
            if not user_record:
                return {'error': 'User not found', 'success': False}
            
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
            
            return {
                'user': user,
                'knowledge_list': user_knowledge,
                'total_knowledge': len(user_knowledge),
                'success': True
            }

    def update_user_knowledge_progress(self, user_id: str, knowledge_id: str, progress: int = None, status: str = None) -> Dict[str, Any]:
        """
        Update user's progress on specific knowledge
        
        Args:
            user_id: User ID
            knowledge_id: Knowledge ID
            progress: Progress percentage (0-100)
            status: Learning status
            
        Returns:
            Dictionary with updated relationship info
        """
        with self.driver.session() as session:
            # Check if relationship exists
            rel_check = session.run("""
                MATCH (u:User {id: $user_id})-[r:LEARNED]->(k:Knowledge {id: $knowledge_id})
                RETURN r, u.name as user_name, k.name as knowledge_name
            """, user_id=user_id, knowledge_id=knowledge_id)
            
            rel_record = rel_check.single()
            if not rel_record:
                return {'error': 'User-Knowledge relationship not found', 'success': False}
            
            # Update relationship
            update_data = {
                'user_id': user_id,
                'knowledge_id': knowledge_id,
                'updatedAt': datetime.now().isoformat()
            }
            
            # Add optional updates
            if progress is not None:
                update_data['progress'] = min(100, max(0, int(progress)))
            
            if status is not None:
                allowed_statuses = ['learning', 'completed', 'mastered', 'reviewing']
                if status in allowed_statuses:
                    update_data['status'] = status
            
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
            
            return {
                'message': 'User knowledge progress updated',
                'update': {
                    'user_name': updated_record['user_name'],
                    'knowledge_name': updated_record['knowledge_name'],
                    'relationship': updated_relationship
                },
                'success': True
            }

    # ==================== HIERARCHY MANAGEMENT ====================
    
    def get_subjects(self) -> Dict[str, Any]:
        """Get all subjects"""
        with self.driver.session() as session:
            result = session.run("MATCH (s:Subject) RETURN s ORDER BY s.name")
            subjects = [dict(record["s"].items()) for record in result]
        return {'subjects': subjects, 'count': len(subjects), 'success': True}

    def get_typebooks(self, subject_id: str = None) -> Dict[str, Any]:
        """Get typebooks with optional subject filter"""
        with self.driver.session() as session:
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
        
        return {'typebooks': typebooks, 'count': len(typebooks), 'success': True}

    def get_chapters(self, typebook_id: str = None) -> Dict[str, Any]:
        """Get chapters with optional typebook filter"""
        with self.driver.session() as session:
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
        
        return {'chapters': chapters, 'count': len(chapters), 'success': True}

    def get_lessons(self, chapter_id: str = None) -> Dict[str, Any]:
        """Get lessons with optional chapter filter"""
        with self.driver.session() as session:
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
        
        return {'lessons': lessons, 'count': len(lessons), 'success': True}

    # ==================== EXPORT/IMPORT ====================
    
    def export_all_data(self) -> Dict[str, Any]:
        """Export all system data"""
        with self.driver.session() as session:
            # Get users
            users_result = session.run("MATCH (u:User) RETURN u")
            users = [dict(record["u"].items()) for record in users_result]
            
            # Get tests with questions and answers
            tests_result = session.run("""
                MATCH (u:User)-[:TOOK]->(t:Test)
                OPTIONAL MATCH (t)-[:CONTAINS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(a:TestAnswer)
                RETURN t, u.id as user_id, u.name as user_name,
                       collect({
                           question: q,
                           answer: a
                       }) as qa_pairs
            """)
            
            tests = []
            for record in tests_result:
                test = dict(record["t"].items())
                test['user_id'] = record['user_id']
                test['user_name'] = record['user_name']
                test['questions_and_answers'] = [
                    {
                        'question': dict(qa['question'].items()) if qa['question'] else None,
                        'answer': dict(qa['answer'].items()) if qa['answer'] else None
                    } for qa in record['qa_pairs'] if qa['question']
                ]
                tests.append(test)
            
            # Get knowledge relationships
            knowledge_result = session.run("""
                MATCH (u:User)-[r:LEARNED]->(k:Knowledge)
                RETURN u.id as user_id, u.name as user_name,
                       k, r
            """)
            
            knowledge_links = []
            for record in knowledge_result:
                link = {
                    'user_id': record['user_id'],
                    'user_name': record['user_name'],
                    'knowledge': dict(record["k"].items()),
                    'relationship': dict(record["r"].items())
                }
                knowledge_links.append(link)
            
            return {
                'users': users,
                'tests': tests,
                'knowledge_links': knowledge_links,
                'summary': {
                    'total_users': len(users),
                    'total_tests': len(tests),
                    'total_knowledge_links': len(knowledge_links)
                },
                'exported_at': datetime.now().isoformat(),
                'success': True
            }

    # ==================== UTILITY METHODS ====================
    
    def delete_test(self, test_id: str) -> Dict[str, Any]:
        """
        Delete a test and all related data
        
        Args:
            test_id: Test ID to delete
            
        Returns:
            Dictionary with deletion status
        """
        with self.driver.session() as session:
            # Check if test exists
            test_check = session.run("MATCH (t:Test {id: $test_id}) RETURN t", test_id=test_id)
            if not test_check.single():
                return {'error': 'Test not found', 'success': False}
            
            # Delete test and all related nodes
            result = session.run("""
                MATCH (t:Test {id: $test_id})-[:CONTAINS_QUESTION]->(q:Question)-[:HAS_ANSWER]->(a:TestAnswer)
                DETACH DELETE t, q, a
                RETURN count(*) as deleted_count
            """, test_id=test_id)
            
            return {
                'message': 'Test and related data deleted successfully',
                'test_id': test_id,
                'success': True
            }

    def cleanup_orphaned_nodes(self) -> Dict[str, Any]:
        """
        Clean up orphaned nodes (nodes without relationships)
        
        Returns:
            Dictionary with cleanup statistics
        """
        with self.driver.session() as session:
            # Find and delete orphaned questions (not connected to tests or lessons)
            orphaned_questions = session.run("""
                MATCH (q:Question)
                WHERE NOT (q)-[:HAS_ANSWER]-() AND NOT (q)<-[:CONTAINS_QUESTION]-() AND NOT (q)-[:BELONGS_TO_LESSON]->()
                DETACH DELETE q
                RETURN count(q) as deleted_questions
            """)
            
            # Find and delete orphaned test answers (not connected to questions)
            orphaned_answers = session.run("""
                MATCH (a:TestAnswer)
                WHERE NOT (a)<-[:HAS_ANSWER]-()
                DETACH DELETE a
                RETURN count(a) as deleted_answers
            """)
            
            q_count = orphaned_questions.single()['deleted_questions']
            a_count = orphaned_answers.single()['deleted_answers']
            
            return {
                'message': 'Cleanup completed',
                'deleted_questions': q_count,
                'deleted_answers': a_count,
                'total_deleted': q_count + a_count,
                'success': True
            }


# ==================== USAGE EXAMPLES ====================

def main():
    """Example usage of the EducationSystem class"""
    
    # Initialize the system
    edu_system = EducationSystem()
    
    try:
        # Health check
        health = edu_system.health_check()
        print("🏥 Health Check:", health)
        
        # Create a user
        user_result = edu_system.create_user(
            name="Nguyễn Văn A",
            email="student_a@example.com",
            age=8
        )
        print("👤 User Created:", user_result)
        
        if user_result['success']:
            user_id = user_result['user']['id']
            
            # Create a test with questions
            test_questions = [
                {
                    "question": "2 + 3 bằng bao nhiêu?",
                    "answer": "5",
                    "student_answer": "5",
                    "is_correct": True,
                    "points": 1,
                    "difficulty": "easy",
                    "duration_seconds": 30
                },
                {
                    "question": "Đếm số lượng quả táo trong hình?",
                    "answer": "4 quả táo",
                    "image_question": "images/apples.jpg",
                    "student_answer": "3 quả",
                    "is_correct": False,
                    "points": 2,
                    "difficulty": "medium",
                    "duration_seconds": 45
                }
            ]
            
            test_result = edu_system.create_complete_test(
                title="Bài kiểm tra Toán cơ bản",
                description="Test các phép tính đơn giản",
                user_id=user_id,
                questions=test_questions,
                duration_minutes=30
            )
            print("📝 Test Created:", test_result)
            
            # Get user's test history
            history = edu_system.get_user_test_history(user_id)
            print("📊 Test History:", history)
            
            # Get user analytics
            analytics = edu_system.get_user_analytics(user_id)
            print("📈 User Analytics:", analytics)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Close connection
        edu_system.close()


if __name__ == "__main__":
    main()