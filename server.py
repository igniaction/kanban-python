import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from database import (
    create_database,
    add_task,
    list_tasks,
    update_task_status,
    delete_task
)

ASSETS_DIR = "assets"


class KanbanHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        """
        Redireciona arquivos estáticos para a pasta /assets
        """
        parsed_path = urlparse(path).path

        if parsed_path.startswith("/api"):
            return path

        if parsed_path == "/":
            parsed_path = "/index.html"

        return os.path.join(os.getcwd(), ASSETS_DIR, parsed_path.lstrip("/"))

    def _send_json(self, data, status=200):
        response = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(body)

    def do_GET(self):
        if self.path == "/api/tasks":
            tasks = list_tasks()
            self._send_json(tasks)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/tasks":
            try:
                data = self._read_json_body()
                title = data.get("title")
                description = data.get("description")

                if not title:
                    self._send_json({"error": "Title is required"}, status=400)
                    return

                add_task(title, description)
                self._send_json({"message": "Task created"}, status=201)

            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404)

    def do_PUT(self):
        if self.path == "/api/tasks":
            try:
                data = self._read_json_body()
                task_id = data.get("id")
                new_status = data.get("status")

                if not task_id or not new_status:
                    self._send_json(
                        {"error": "id and status are required"},
                        status=400
                    )
                    return

                update_task_status(task_id, new_status)
                self._send_json({"message": "Task updated"})

            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path == "/api/tasks":
            try:
                data = self._read_json_body()
                task_id = data.get("id")

                if not task_id:
                    self._send_json({"error": "id is required"}, status=400)
                    return

                delete_task(task_id)
                self._send_json({"message": "Task deleted"})

            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(404)


def run_server(host="localhost", port=8000):
    create_database()
    server = HTTPServer((host, port), KanbanHandler)
    print(f"Servidor rodando em http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
