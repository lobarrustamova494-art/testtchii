"""
MongoDB Database Service
Async database operations for OMR system
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    MongoDB database service with async operations
    """
    
    def __init__(
        self,
        connection_string: str = None,
        database_name: str = "evalbee_omr"
    ):
        self.connection_string = connection_string or os.getenv(
            'MONGODB_URL', 
            'mongodb://localhost:27017'
        )
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.database_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            users_collection = self.db.users
            await users_collection.create_index("username", unique=True)
            await users_collection.create_index("email", unique=True)
            
            # Exams collection indexes
            exams_collection = self.db.exams
            await exams_collection.create_index("created_by")
            await exams_collection.create_index("created_at")
            await exams_collection.create_index([("name", "text")])
            
            # Results collection indexes
            results_collection = self.db.grading_results
            await results_collection.create_index("exam_id")
            await results_collection.create_index("graded_by")
            await results_collection.create_index("created_at")
            
            # Answer keys collection indexes
            answer_keys_collection = self.db.answer_keys
            await answer_keys_collection.create_index("exam_id", unique=True)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    # User Management
    async def create_user(self, user_data: Dict) -> str:
        """Create new user"""
        try:
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            
            result = await self.db.users.insert_one(user_data)
            logger.info(f"User created: {user_data['username']}")
            return str(result.inserted_id)
            
        except DuplicateKeyError:
            raise ValueError("Username or email already exists")
    
    async def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return await self.db.users.find_one({"username": username})
    
    async def update_user(self, username: str, update_data: Dict) -> bool:
        """Update user data"""
        update_data['updated_at'] = datetime.utcnow()
        
        result = await self.db.users.update_one(
            {"username": username},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """List all users (admin only)"""
        cursor = self.db.users.find(
            {},
            {"password_hash": 0}  # Exclude password hash
        ).skip(skip).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    # Exam Management
    async def create_exam(self, exam_data: Dict) -> str:
        """Create new exam"""
        exam_data['created_at'] = datetime.utcnow()
        exam_data['updated_at'] = datetime.utcnow()
        
        result = await self.db.exams.insert_one(exam_data)
        logger.info(f"Exam created: {exam_data['name']}")
        return str(result.inserted_id)
    
    async def get_exam(self, exam_id: str) -> Optional[Dict]:
        """Get exam by ID"""
        from bson import ObjectId
        return await self.db.exams.find_one({"_id": ObjectId(exam_id)})
    
    async def list_exams(
        self, 
        created_by: str = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict]:
        """List exams"""
        filter_query = {}
        if created_by:
            filter_query['created_by'] = created_by
        
        cursor = self.db.exams.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def update_exam(self, exam_id: str, update_data: Dict) -> bool:
        """Update exam"""
        from bson import ObjectId
        update_data['updated_at'] = datetime.utcnow()
        
        result = await self.db.exams.update_one(
            {"_id": ObjectId(exam_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def delete_exam(self, exam_id: str) -> bool:
        """Delete exam"""
        from bson import ObjectId
        result = await self.db.exams.delete_one({"_id": ObjectId(exam_id)})
        return result.deleted_count > 0
    
    # Answer Key Management
    async def save_answer_key(self, exam_id: str, answer_key: Dict, created_by: str) -> str:
        """Save answer key for exam"""
        answer_key_data = {
            'exam_id': exam_id,
            'answer_key': answer_key,
            'created_by': created_by,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Use upsert to replace existing answer key
        result = await self.db.answer_keys.replace_one(
            {"exam_id": exam_id},
            answer_key_data,
            upsert=True
        )
        
        logger.info(f"Answer key saved for exam: {exam_id}")
        return str(result.upserted_id) if result.upserted_id else exam_id
    
    async def get_answer_key(self, exam_id: str) -> Optional[Dict]:
        """Get answer key for exam"""
        return await self.db.answer_keys.find_one({"exam_id": exam_id})
    
    # Grading Results Management
    async def save_grading_result(self, result_data: Dict) -> str:
        """Save grading result"""
        result_data['created_at'] = datetime.utcnow()
        
        result = await self.db.grading_results.insert_one(result_data)
        logger.info(f"Grading result saved for exam: {result_data.get('exam_id')}")
        return str(result.inserted_id)
    
    async def get_grading_result(self, result_id: str) -> Optional[Dict]:
        """Get grading result by ID"""
        from bson import ObjectId
        return await self.db.grading_results.find_one({"_id": ObjectId(result_id)})
    
    async def list_grading_results(
        self,
        exam_id: str = None,
        graded_by: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """List grading results"""
        filter_query = {}
        if exam_id:
            filter_query['exam_id'] = exam_id
        if graded_by:
            filter_query['graded_by'] = graded_by
        
        cursor = self.db.grading_results.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    # Statistics and Analytics
    async def get_exam_statistics(self, exam_id: str) -> Dict:
        """Get statistics for an exam"""
        pipeline = [
            {"$match": {"exam_id": exam_id}},
            {"$group": {
                "_id": None,
                "total_attempts": {"$sum": 1},
                "avg_score": {"$avg": "$results.percentage"},
                "max_score": {"$max": "$results.percentage"},
                "min_score": {"$min": "$results.percentage"},
                "total_questions": {"$first": "$results.totalQuestions"},
                "avg_correct": {"$avg": "$results.correctAnswers"}
            }}
        ]
        
        cursor = self.db.grading_results.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        return result[0] if result else {}
    
    async def get_user_statistics(self, username: str) -> Dict:
        """Get statistics for a user"""
        pipeline = [
            {"$match": {"graded_by": username}},
            {"$group": {
                "_id": None,
                "total_graded": {"$sum": 1},
                "unique_exams": {"$addToSet": "$exam_id"},
                "avg_processing_time": {"$avg": "$statistics.duration"},
                "total_ai_verifications": {"$sum": "$statistics.ai.verified"}
            }},
            {"$addFields": {
                "unique_exams_count": {"$size": "$unique_exams"}
            }}
        ]
        
        cursor = self.db.grading_results.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        return result[0] if result else {}
    
    # Health Check
    async def health_check(self) -> Dict:
        """Database health check"""
        try:
            # Test connection
            await self.client.admin.command('ping')
            
            # Get collection stats
            stats = {
                'status': 'healthy',
                'database': self.database_name,
                'collections': {
                    'users': await self.db.users.count_documents({}),
                    'exams': await self.db.exams.count_documents({}),
                    'answer_keys': await self.db.answer_keys.count_documents({}),
                    'grading_results': await self.db.grading_results.count_documents({})
                }
            }
            
            return stats
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

# Global database instance
db_service = DatabaseService()