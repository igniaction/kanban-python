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
        Redireciona arquivos estáticos para a pasta /assets.
        Rotas de API e Health não passam por aqui pois são interceptadas antes.
        """
        parsed_path = urlparse(path).path

        # Se for API ou Health, não tentamos traduzir para caminho de arquivo
        if parsed_path.startswith("/api") or parsed_path == "/health":
            return path

        if parsed_path == "/":
            parsed_path = "/index.html"

        return os.path.join(os.getcwd(), ASSETS_DIR, parsed_path.lstrip("/"))

    def _send_json(self, data, status=200):
        """Auxiliar para responder com JSON e headers corretos"""
        response = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _read_json_body(self):
        """Auxiliar para ler o corpo da requisição"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(body)

    def do_GET(self):
        """
        Manipula requisições GET.
        Ordem de verificação:
        1. Health Check (Vital para K8s/Monitoramento)
        2. API de Tarefas
        3. Arquivos Estáticos (Frontend)
        """
        
        # --- NOVO ENDPOINT: HEALTH CHECK ---
        if self.path == "/health":
            # Responde 200 OK imediatamente.
            # Em cenários reais, você poderia testar a conexão com o DB aqui.
            self._send_json({"status": "ok"})
            return
        # -----------------------------------

        if self.path == "/api/tasks":
            tasks = list_tasks()
            self._send_json(tasks)
        else:
            # Se não for API nem Health, tenta servir arquivo estático (HTML/CSS/JS)
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
    print(f"Health check disponível em http://{host}:{port}/health")
    server.serve_forever()


if __name__ == "__main__":
    run_server()