import hashlib
import datetime
from .connection import get_connection

class User:
    @staticmethod
    def create(phone_number, name, email, password):
        """
        Create a new user in the database.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Hash the password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Insert the user
            cursor.execute("""
            INSERT INTO users (phone_number, name, email, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING id, phone_number, name, email, created_at;
            """, (phone_number, name, email, password_hash))
            
            user = cursor.fetchone()
            conn.commit()
            
            return {
                'id': user[0],
                'phone_number': user[1],
                'name': user[2],
                'email': user[3],
                'created_at': user[4].isoformat(),
            }
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def authenticate(phone_number, password):
        """
        Authenticate a user by phone number and password.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Hash the password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Find the user
            cursor.execute("""
            SELECT id, phone_number, name, email, created_at
            FROM users
            WHERE phone_number = %s AND password_hash = %s;
            """, (phone_number, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'phone_number': user[1],
                    'name': user[2],
                    'email': user[3],
                    'created_at': user[4].isoformat(),
                }
            else:
                return None
        except Exception as e:
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        """
        Get a user by ID.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, phone_number, name, email, created_at
            FROM users
            WHERE id = %s;
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'phone_number': user[1],
                    'name': user[2],
                    'email': user[3],
                    'created_at': user[4].isoformat(),
                }
            else:
                return None
        except Exception as e:
            raise
        finally:
            if conn:
                conn.close()

class Device:
    @staticmethod
    def create(user_id, device_name, device_id):
        """
        Create a new device in the database.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO devices (user_id, device_name, device_id)
            VALUES (%s, %s, %s)
            RETURNING id, user_id, device_name, device_id, is_active, created_at;
            """, (user_id, device_name, device_id))
            
            device = cursor.fetchone()
            conn.commit()
            
            return {
                'id': device[0],
                'user_id': device[1],
                'device_name': device[2],
                'device_id': device[3],
                'is_active': device[4],
                'created_at': device[5].isoformat(),
            }
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_by_user_id(user_id):
        """
        Get all devices for a user.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, user_id, device_name, device_id, is_active, created_at
            FROM devices
            WHERE user_id = %s;
            """, (user_id,))
            
            devices = cursor.fetchall()
            
            return [{
                'id': device[0],
                'user_id': device[1],
                'device_name': device[2],
                'device_id': device[3],
                'is_active': device[4],
                'created_at': device[5].isoformat(),
            } for device in devices]
        except Exception as e:
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update(device_id, device_name=None, is_active=None):
        """
        Update a device in the database.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            update_fields = []
            params = []
            
            if device_name is not None:
                update_fields.append("device_name = %s")
                params.append(device_name)
            
            if is_active is not None:
                update_fields.append("is_active = %s")
                params.append(is_active)
            
            if not update_fields:
                return None
            
            params.append(device_id)
            
            cursor.execute(f"""
            UPDATE devices
            SET {", ".join(update_fields)}
            WHERE id = %s
            RETURNING id, user_id, device_name, device_id, is_active, created_at;
            """, params)
            
            device = cursor.fetchone()
            conn.commit()
            
            if device:
                return {
                    'id': device[0],
                    'user_id': device[1],
                    'device_name': device[2],
                    'device_id': device[3],
                    'is_active': device[4],
                    'created_at': device[5].isoformat(),
                }
            else:
                return None
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def delete(device_id):
        """
        Delete a device from the database.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            DELETE FROM devices
            WHERE id = %s
            RETURNING id;
            """, (device_id,))
            
            result = cursor.fetchone()
            conn.commit()
            
            return result is not None
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

class Location:
    @staticmethod
    def create(device_id, latitude, longitude, accuracy=None, speed=None, heading=None, altitude=None):
        """
        Create a new location record in the database.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO locations (device_id, latitude, longitude, accuracy, speed, heading, altitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, device_id, latitude, longitude, timestamp, accuracy, speed, heading, altitude;
            """, (device_id, latitude, longitude, accuracy, speed, heading, altitude))
            
            location = cursor.fetchone()
            conn.commit()
            
            return {
                'id': location[0],
                'device_id': location[1],
                'latitude': location[2],
                'longitude': location[3],
                'timestamp': location[4].isoformat(),
                'accuracy': location[5],
                'speed': location[6],
                'heading': location[7],
                'altitude': location[8],
            }
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_current(device_id):
        """
        Get the most recent location for a device.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, device_id, latitude, longitude, timestamp, accuracy, speed, heading, altitude
            FROM locations
            WHERE device_id = %s
            ORDER BY timestamp DESC
            LIMIT 1;
            """, (device_id,))
            
            location = cursor.fetchone()
            
            if location:
                return {
                    'id': location[0],
                    'device_id': location[1],
                    'latitude': location[2],
                    'longitude': location[3],
                    'timestamp': location[4].isoformat(),
                    'accuracy': location[5],
                    'speed': location[6],
                    'heading': location[7],
                    'altitude': location[8],
                }
            else:
                return None
        except Exception as e:
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_history(device_id, start_time, end_time):
        """
        Get location history for a device within a time range.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, device_id, latitude, longitude, timestamp, accuracy, speed, heading, altitude
            FROM locations
            WHERE device_id = %s AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp ASC;
            """, (device_id, start_time, end_time))
            
            locations = cursor.fetchall()
            
            return [{
                'id': location[0],
                'device_id': location[1],
                'latitude': location[2],
                'longitude': location[3],
                'timestamp': location[4].isoformat(),
                'accuracy': location[5],
                'speed': location[6],
                'heading': location[7],
                'altitude': location[8],
            } for location in locations]
        except Exception as e:
            raise
        finally:
            if conn:
                conn.close()

class Session:
    @staticmethod
    def create(user_id, notes=None):
        """
        Create a new tracking session.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO sessions (user_id, notes)
            VALUES (%s, %s)
            RETURNING id, user_id, start_time, end_time, notes;
            """, (user_id, notes))
            
            session = cursor.fetchone()
            conn.commit()
            
            return {
                'id': session[0],
                'user_id': session[1],
                'start_time': session[2].isoformat(),
                'end_time': session[3].isoformat() if session[3] else None,
                'notes': session[4],
            }
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def end_session(session_id, notes=None):
        """
        End a tracking session.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            update_query = """
            UPDATE sessions
            SET end_time = CURRENT_TIMESTAMP
            """
            
            params = []
            
            if notes is not None:
                update_query += ", notes = %s"
                params.append(notes)
            
            update_query += """
            WHERE id = %s AND end_time IS NULL
            RETURNING id, user_id, start_time, end_time, notes;
            """
            
            params.append(session_id)
            
            cursor.execute(update_query, params)
            
            session = cursor.fetchone()
            conn.commit()
            
            if session:
                return {
                    'id': session[0],
                    'user_id': session[1],
                    'start_time': session[2].isoformat(),
                    'end_time': session[3].isoformat() if session[3] else None,
                    'notes': session[4],
                }
            else:
                return None
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_by_user_id(user_id):
        """
        Get all sessions for a user.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, user_id, start_time, end_time, notes
            FROM sessions
            WHERE user_id = %s
            ORDER BY start_time DESC;
            """, (user_id,))
            
            sessions = cursor.fetchall()
            
            return [{
                'id': session[0],
                'user_id': session[1],
                'start_time': session[2].isoformat(),
                'end_time': session[3].isoformat() if session[3] else None,
                'notes': session[4],
            } for session in sessions]
        except Exception as e:
            raise
        finally:
            if conn:
                conn.close()
