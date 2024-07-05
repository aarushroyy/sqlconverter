from http.server import BaseHTTPRequestHandler
import json
import cgi
import io
import sys
import traceback
sys.path.append('/var/task')
from generate_er_diagram import parse_sql, generate_er_diagram

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            if 'sqlFile' not in form:
                raise ValueError('No file uploaded')

            sql_file = form['sqlFile']
            sql_content = sql_file.file.read().decode('utf-8')

            tables = parse_sql(io.StringIO(sql_content))
            png_data = generate_er_diagram(tables)

            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(png_data)
        except Exception as e:
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