from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import User, Role, db
# Import tasks inside functions to avoid circular import
# from celery_app import export_quiz_history_csv, export_user_performance_csv, export_quiz_analytics_csv
import os
from datetime import datetime

export_bp = Blueprint('export', __name__)

@export_bp.route('/export/quiz-history', methods=['POST'])
@jwt_required()
def export_quiz_history():
    """User-triggered export of their quiz history"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get export format from request
        data = request.get_json() or {}
        export_format = data.get('format', 'csv')
        
        if export_format not in ['csv', 'excel']:
            return jsonify({"error": "Invalid export format. Use 'csv' or 'excel'"}), 400
        
        # Trigger async export task
        from celery_app import export_quiz_history_csv
        task = export_quiz_history_csv.delay(current_user_id, export_format)
        
        return jsonify({
            "message": "Export started successfully",
            "task_id": task.id,
            "status": "processing",
            "user": user.username,
            "format": export_format
        }), 202
    
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@export_bp.route('/export/user-performance', methods=['POST'])
@jwt_required()
def export_user_performance():
    """Admin-triggered export of user performance data"""
    try:
        current_user_id = get_jwt_identity()
        admin = User.query.get(current_user_id)
        
        if not admin or admin.role != Role.ADMIN:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Get export parameters from request
        data = request.get_json() or {}
        export_format = data.get('format', 'csv')
        filters = data.get('filters', {})
        
        if export_format not in ['csv', 'excel']:
            return jsonify({"error": "Invalid export format. Use 'csv' or 'excel'"}), 400
        
        # Validate and parse date filters
        if filters.get('date_from'):
            try:
                filters['date_from'] = datetime.fromisoformat(filters['date_from'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date_from format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
        
        if filters.get('date_to'):
            try:
                filters['date_to'] = datetime.fromisoformat(filters['date_to'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date_to format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
        
        # Trigger async export task
        from celery_app import export_user_performance_csv
        task = export_user_performance_csv.delay(current_user_id, filters, export_format)
        
        return jsonify({
            "message": "User performance export started successfully",
            "task_id": task.id,
            "status": "processing",
            "admin": admin.username,
            "format": export_format,
            "filters": filters
        }), 202
    
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@export_bp.route('/export/quiz-analytics', methods=['POST'])
@jwt_required()
def export_quiz_analytics():
    """Admin-triggered export of detailed quiz analytics"""
    try:
        current_user_id = get_jwt_identity()
        admin = User.query.get(current_user_id)
        
        if not admin or admin.role != Role.ADMIN:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Get export parameters from request
        data = request.get_json() or {}
        export_format = data.get('format', 'csv')
        quiz_id = data.get('quiz_id')  # Optional: specific quiz or all quizzes
        
        if export_format not in ['csv', 'excel']:
            return jsonify({"error": "Invalid export format. Use 'csv' or 'excel'"}), 400
        
        # Trigger async export task
        from celery_app import export_quiz_analytics_csv
        task = export_quiz_analytics_csv.delay(current_user_id, quiz_id, export_format)
        
        return jsonify({
            "message": "Quiz analytics export started successfully",
            "task_id": task.id,
            "status": "processing",
            "admin": admin.username,
            "format": export_format,
            "quiz_id": quiz_id
        }), 202
    
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@export_bp.route('/export/status/<task_id>', methods=['GET'])
@jwt_required()
def get_export_status(task_id):
    """Get the status of an export task"""
    try:
        # Import celery inside function to avoid circular import
        from celery_app import celery
        
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Task is pending...'
            }
        elif task.state == 'SUCCESS':
            result = task.result
            if isinstance(result, dict) and result.get('error'):
                response = {
                    'state': 'FAILURE',
                    'status': result['error']
                }
            else:
                response = {
                    'state': task.state,
                    'status': 'Export completed successfully',
                    'result': result
                }
        elif task.state == 'FAILURE':
            response = {
                'state': task.state,
                'status': str(task.info)
            }
        else:
            response = {
                'state': task.state,
                'status': 'Task is running...'
            }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": f"Failed to get task status: {str(e)}"}), 500

@export_bp.route('/export/download/<filename>', methods=['GET'])
@jwt_required()
def download_export(filename):
    """Download a completed export file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Security check: only allow downloading files from exports directory
        if '..' in filename or '/' in filename:
            return jsonify({"error": "Invalid filename"}), 400
        
        filepath = os.path.join('exports', filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        # For admin users, allow downloading any export
        # For regular users, only allow downloading their own quiz history exports
        if user.role != Role.ADMIN:
            if not filename.startswith(f"quiz_history_{user.username}_"):
                return jsonify({"error": "Unauthorized access to this file"}), 403
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv' if filename.endswith('.csv') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@export_bp.route('/export/list', methods=['GET'])
@jwt_required()
def list_exports():
    """List available export files for the user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        exports_dir = 'exports'
        if not os.path.exists(exports_dir):
            return jsonify({"exports": []})
        
        files = []
        for filename in os.listdir(exports_dir):
            filepath = os.path.join(exports_dir, filename)
            if os.path.isfile(filepath):
                # For admin users, show all files
                # For regular users, only show their own quiz history exports
                if user.role == Role.ADMIN or filename.startswith(f"quiz_history_{user.username}_"):
                    file_stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'size': file_stat.st_size,
                        'created': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({"exports": files})
    
    except Exception as e:
        return jsonify({"error": f"Failed to list exports: {str(e)}"}), 500

@export_bp.route('/export/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete_export(filename):
    """Delete an export file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Security check: only allow deleting files from exports directory
        if '..' in filename or '/' in filename:
            return jsonify({"error": "Invalid filename"}), 400
        
        filepath = os.path.join('exports', filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        # For admin users, allow deleting any export
        # For regular users, only allow deleting their own quiz history exports
        if user.role != Role.ADMIN:
            if not filename.startswith(f"quiz_history_{user.username}_"):
                return jsonify({"error": "Unauthorized access to this file"}), 403
        
        os.remove(filepath)
        
        return jsonify({"message": "Export file deleted successfully"})
    
    except Exception as e:
        return jsonify({"error": f"Delete failed: {str(e)}"}), 500 