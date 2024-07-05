from http.server import BaseHTTPRequestHandler
import json
import cgi
import io
import sys
import traceback
import os
import logging
sys.path.append('/var/task')
from generate_er_diagram import parse_sql, generate_er_diagram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            logger.info("Received POST request")
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            if 'sqlFile' not in form:
                raise ValueError('No file uploaded')

            logger.info("File found in form")
            sql_file = form['sqlFile']
            sql_content = sql_file.file.read().decode('utf-8')

            logger.info("SQL content read")
            tables = parse_sql(io.StringIO(sql_content))
            logger.info("SQL parsed")
            png_data = generate_er_diagram(tables)
            logger.info("ER diagram generated")

            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(png_data)
            logger.info("Response sent successfully")
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, 'Internal Server Error')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_message = str(e)
            tb = traceback.format_exc()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'Error processing file: {error_message}',
                'traceback': tb
            }).encode('utf-8'))

    def do_GET(self):
        self.send_error(405, 'Method Not Allowed')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': False,
            'message': 'Method Not Allowed'
        }).encode('utf-8'))