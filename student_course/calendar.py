from flask import Blueprint, Flask, flash, render_template, request, jsonify
import pymysql
from database.connect import get_db_connection

calendar_bp = Blueprint('calendar', __name__, template_folder='templates')

@calendar_bp.route('/')
def index():
    return render_template('calendar/calendar.html')

@calendar_bp.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cur.execute("SELECT id, title, start_event as start, end_event as end FROM events ORDER BY id")
        events = cur.fetchall()
        return jsonify([dict(event) for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@calendar_bp.route('/api/events', methods=['POST'])
def create_event():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        data = request.form
        cur.execute(
            "INSERT INTO events (title, start_event, end_event) VALUES (%s, %s, %s)",
            [data['title'], data['start'], data['end']]
        )
        # 取得最後插入的 ID
        event_id = cur.lastrowid
        conn.commit()
        return jsonify({'id': event_id, 'message': 'Event created successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@calendar_bp.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        data = request.get_json()  # Parse JSON data
        cur.execute(
            "UPDATE events SET title = %s, start_event = %s, end_event = %s WHERE id = %s",
            [data['title'], data['start'], data['end'], event_id]
        )
        event_id = cur.lastrowid
        conn.commit()
        return jsonify({'id': event_id, 'message': 'Event created successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()



@calendar_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM events WHERE id = %s", [event_id])
        conn.commit()
        return jsonify({'message': 'Event deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()