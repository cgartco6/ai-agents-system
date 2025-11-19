import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import os

class KnowledgeBase:
    """Structured knowledge base for storing and retrieving information"""
    
    def __init__(self, db_path: str = "data/knowledge_base.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Core knowledge table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                source TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                relationship_type TEXT,
                strength REAL DEFAULT 1.0,
                FOREIGN KEY (source_id) REFERENCES knowledge_entries (id),
                FOREIGN KEY (target_id) REFERENCES knowledge_entries (id)
            )
        ''')
        
        # Metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_metadata (
                entry_id TEXT,
                key TEXT,
                value TEXT,
                PRIMARY KEY (entry_id, key),
                FOREIGN KEY (entry_id) REFERENCES knowledge_entries (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def add_knowledge(self, title: str, content: str, category: str = "general", 
                          tags: List[str] = None, source: str = "system", 
                          confidence: float = 1.0, metadata: Dict[str, Any] = None) -> str:
        """Add knowledge entry to the database"""
        entry_id = self._generate_id(title, content)
        tags_json = json.dumps(tags or [])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert or update knowledge entry
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge_entries 
            (id, title, content, category, tags, source, confidence, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, title, content, category, tags_json, source, confidence, datetime.now()))
        
        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_metadata (entry_id, key, value)
                    VALUES (?, ?, ?)
                ''', (entry_id, key, json.dumps(value)))
        
        conn.commit()
        conn.close()
        
        return entry_id
    
    async def get_knowledge(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve knowledge entry by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM knowledge_entries WHERE id = ?
        ''', (entry_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        # Get metadata
        cursor.execute('''
            SELECT key, value FROM knowledge_metadata WHERE entry_id = ?
        ''', (entry_id,))
        
        metadata = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'id': row[0],
            'title': row[1],
            'content': row[2],
            'category': row[3],
            'tags': json.loads(row[4]),
            'source': row[5],
            'confidence': row[6],
            'created_at': row[7],
            'updated_at': row[8],
            'access_count': row[9],
            'metadata': metadata
        }
    
    async def search_knowledge(self, query: str, category: str = None, 
                             tags: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge entries by query, category, and tags"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        sql = '''
            SELECT * FROM knowledge_entries 
            WHERE (title LIKE ? OR content LIKE ?)
        '''
        params = [f'%{query}%', f'%{query}%']
        
        if category:
            sql += ' AND category = ?'
            params.append(category)
        
        if tags:
            placeholders = ','.join('?' * len(tags))
            sql += f' AND tags LIKE ?'  # Simplified tag search
            for tag in tags:
                params.append(f'%{tag}%')
        
        sql += ' ORDER BY access_count DESC, updated_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'tags': json.loads(row[4]),
                'source': row[5],
                'confidence': row[6],
                'created_at': row[7],
                'updated_at': row[8],
                'access_count': row[9]
            })
            
            # Update access count
            cursor.execute('''
                UPDATE knowledge_entries SET access_count = access_count + 1 
                WHERE id = ?
            ''', (row[0],))
        
        conn.commit()
        conn.close()
        
        return results
    
    async def create_relationship(self, source_id: str, target_id: str, 
                                relationship_type: str, strength: float = 1.0):
        """Create relationship between knowledge entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO knowledge_relationships 
            (source_id, target_id, relationship_type, strength)
            VALUES (?, ?, ?, ?)
        ''', (source_id, target_id, relationship_type, strength))
        
        conn.commit()
        conn.close()
    
    async def get_related_knowledge(self, entry_id: str, 
                                  relationship_type: str = None) -> List[Dict[str, Any]]:
        """Get knowledge entries related to the given entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = '''
            SELECT ke.*, kr.relationship_type, kr.strength
            FROM knowledge_entries ke
            JOIN knowledge_relationships kr ON ke.id = kr.target_id
            WHERE kr.source_id = ?
        '''
        params = [entry_id]
        
        if relationship_type:
            sql += ' AND kr.relationship_type = ?'
            params.append(relationship_type)
        
        sql += ' ORDER BY kr.strength DESC'
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'tags': json.loads(row[4]),
                'source': row[5],
                'confidence': row[6],
                'created_at': row[7],
                'updated_at': row[8],
                'access_count': row[9],
                'relationship_type': row[10],
                'relationship_strength': row[11]
            })
        
        conn.close()
        return results
    
    async def get_knowledge_graph(self, center_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """Get knowledge graph around a central entry"""
        graph = {
            'nodes': [],
            'edges': []
        }
        
        visited = set()
        queue = [(center_id, 0)]  # (node_id, depth)
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if current_id in visited or depth > max_depth:
                continue
                
            visited.add(current_id)
            
            # Get node data
            node_data = await self.get_knowledge(current_id)
            if node_data:
                graph['nodes'].append({
                    'id': node_data['id'],
                    'title': node_data['title'],
                    'category': node_data['category'],
                    'depth': depth
                })
                
                # Get relationships
                relationships = await self.get_related_knowledge(current_id)
                for rel in relationships:
                    graph['edges'].append({
                        'source': current_id,
                        'target': rel['id'],
                        'type': rel['relationship_type'],
                        'strength': rel['relationship_strength']
                    })
                    
                    if rel['id'] not in visited:
                        queue.append((rel['id'], depth + 1))
        
        return graph
    
    async def update_confidence(self, entry_id: str, confidence: float):
        """Update confidence score for knowledge entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE knowledge_entries 
            SET confidence = ?, updated_at = ?
            WHERE id = ?
        ''', (confidence, datetime.now(), entry_id))
        
        conn.commit()
        conn.close()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute('SELECT COUNT(*) FROM knowledge_entries')
        total_entries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_relationships')
        total_relationships = cursor.fetchone()[0]
        
        # Category distribution
        cursor.execute('''
            SELECT category, COUNT(*) 
            FROM knowledge_entries 
            GROUP BY category
        ''')
        category_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) 
            FROM knowledge_entries 
            WHERE updated_at > datetime('now', '-7 days')
        ''')
        recent_updates = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_entries': total_entries,
            'total_relationships': total_relationships,
            'category_distribution': category_distribution,
            'recent_updates_7_days': recent_updates,
            'database_size_mb': self._get_database_size()
        }
    
    def _generate_id(self, title: str, content: str) -> str:
        """Generate unique ID for knowledge entry"""
        content_hash = hashlib.md5(f"{title}{content}".encode()).hexdigest()
        return content_hash[:16]
    
    def _get_database_size(self) -> float:
        """Get database file size in MB"""
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path) / (1024 * 1024)
        return 0.0
    
    async def export_knowledge(self, file_path: str):
        """Export knowledge base to JSON file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all knowledge entries
        cursor.execute('SELECT * FROM knowledge_entries')
        entries = []
        
        for row in cursor.fetchall():
            entry = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'tags': json.loads(row[4]),
                'source': row[5],
                'confidence': row[6],
                'created_at': row[7],
                'updated_at': row[8],
                'access_count': row[9]
            }
            
            # Get metadata
            cursor.execute('SELECT key, value FROM knowledge_metadata WHERE entry_id = ?', (row[0],))
            entry['metadata'] = {meta_row[0]: json.loads(meta_row[1]) for meta_row in cursor.fetchall()}
            
            entries.append(entry)
        
        # Get all relationships
        cursor.execute('SELECT * FROM knowledge_relationships')
        relationships = [
            {
                'source_id': row[1],
                'target_id': row[2],
                'relationship_type': row[3],
                'strength': row[4]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        # Create export data
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'entries': entries,
            'relationships': relationships
        }
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    async def import_knowledge(self, file_path: str):
        """Import knowledge base from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # Import entries
        for entry in import_data.get('entries', []):
            await self.add_knowledge(
                title=entry['title'],
                content=entry['content'],
                category=entry['category'],
                tags=entry['tags'],
                source=entry['source'],
                confidence=entry['confidence'],
                metadata=entry.get('metadata', {})
            )
        
        # Import relationships
        for relationship in import_data.get('relationships', []):
            await self.create_relationship(
                source_id=relationship['source_id'],
                target_id=relationship['target_id'],
                relationship_type=relationship['relationship_type'],
                strength=relationship['strength']
            )
