import importlib
import os

def test_database_crud(tmp_path, monkeypatch):
    # Usa um DB temporário só para este teste
    db_file = tmp_path / "test_kanban.db"
    monkeypatch.setenv("DB_PATH", str(db_file))

    # Recarrega o módulo para ele ler a env var DB_PATH
    import database
    importlib.reload(database)

    # Cria a tabela
    database.create_database()

    # Cria tarefa
    task = database.add_task("Tarefa 1", "Descrição 1")
    assert task["id"] is not None
    assert task["title"] == "Tarefa 1"
    assert task["status"] == "todo"

    # Lista tarefas
    tasks = database.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Tarefa 1"

    # Atualiza status
    ok = database.update_task_status(task["id"], "doing")
    assert ok is True

    tasks2 = database.list_tasks()
    assert tasks2[0]["status"] == "doing"

    # Deleta
    ok2 = database.delete_task(task["id"])
    assert ok2 is True

    tasks3 = database.list_tasks()
    assert tasks3 == []
