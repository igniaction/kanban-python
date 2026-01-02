document.addEventListener("DOMContentLoaded", () => {
    // --- Referências aos elementos ---
    // Usamos os containers internos das colunas para o drop
    const columns = {
        todo: document.getElementById("todo-column"),
        doing: document.getElementById("doing-column"),
        done: document.getElementById("done-column")
    };

    const modalOverlay = document.getElementById("modal-overlay");
    const newTaskBtn = document.getElementById("new-task-btn");
    const cancelBtn = document.getElementById("cancel-btn");
    const taskForm = document.getElementById("task-form");

    const API_URL = "/api/tasks";
    let draggedItem = null; // Variável para armazenar o card sendo arrastado

    /* =======================
       Funções Auxiliares
    ======================= */
    
    // Define qual é o próximo status e o status anterior baseado no atual
    function getAdjacentStatus(currentStatus) {
        const flow = ['todo', 'doing', 'done'];
        const currentIndex = flow.indexOf(currentStatus);
        
        return {
            prev: currentIndex > 0 ? flow[currentIndex - 1] : null,
            next: currentIndex < flow.length - 1 ? flow[currentIndex + 1] : null
        };
    }

    /* =======================
       Modal
    ======================= */
    function openModal() { modalOverlay.classList.remove("hidden"); }
    function closeModal() {
        modalOverlay.classList.add("hidden");
        taskForm.reset();
    }

    newTaskBtn.addEventListener("click", openModal);
    cancelBtn.addEventListener("click", closeModal);
    modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) closeModal(); });

    /* =======================
       API & Lógica de Negócio
    ======================= */

    async function fetchTasks() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) throw new Error("Falha ao buscar tarefas");
            const tasks = await response.json();

            // Limpa as colunas
            Object.values(columns).forEach(col => col.innerHTML = "");

            // Renderiza e distribui as tarefas
            tasks.forEach(task => {
                const card = renderCard(task);
                // Garante que a coluna existe antes de adicionar
                if (columns[task.status]) {
                    columns[task.status].appendChild(card);
                }
            });
        } catch (error) {
            console.error(error);
        }
    }

    async function addTask(event) {
        event.preventDefault();
        const title = document.getElementById("task-title").value.trim();
        const description = document.getElementById("task-description").value.trim();
        if (!title) return;

        try {
            await fetch(API_URL, {
                method: "POST", headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, description, status: "todo" })
            });
            closeModal();
            fetchTasks();
        } catch (error) { console.error(error); }
    }

    // Função central para atualizar o status (usada por clique E por drag & drop)
    async function updateTaskStatus(id, newStatus) {
        try {
            const response = await fetch(API_URL, {
                method: "PUT", headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id, status: newStatus })
            });
            if (!response.ok) throw new Error("Erro ao atualizar status");
            
            // Não precisamos dar fetchTasks() inteiro aqui se usarmos Drag&Drop, 
            // pois moveremos o elemento manualmente no DOM para ser mais rápido.
            // Se for clique no botão, o fetchTasks ajuda a re-renderizar os botões corretos.
            if (!draggedItem) {
                 fetchTasks(); 
            }
        } catch (error) { console.error(error); }
    }

    async function deleteTask(id) {
        if (!confirm("Excluir esta tarefa?")) return;
        try {
            await fetch(API_URL, {
                method: "DELETE", headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id })
            });
            fetchTasks();
        } catch (error) { console.error(error); }
    }

    /* =======================
       Drag and Drop (Implementação do Pedido 1)
    ======================= */

    function setupDraggableCard(card) {
        card.draggable = true; // Habilita o arraste nativo do HTML5

        card.addEventListener('dragstart', function(e) {
            draggedItem = this;
            // Timeout para que o elemento original não suma imediatamente, 
            // mas a "imagem fantasma" do drag apareça.
            setTimeout(() => this.classList.add('dragging'), 0);
            
            // Guardamos o ID do card para usar no drop
            e.dataTransfer.effectAllowed = 'move';
            // Usamos dataset.id que adicionamos no renderCard
            e.dataTransfer.setData('text/plain', this.dataset.id); 
        });

        card.addEventListener('dragend', function() {
            this.classList.remove('dragging');
            draggedItem = null;
             // Remove highlights de todas as colunas ao terminar
            Object.values(columns).forEach(col => col.classList.remove('drag-over'));
        });
    }

    // Configura os listeners nas colunas (áreas de drop)
    Object.entries(columns).forEach(([statusKey, columnElement]) => {
        
        // 'dragover' é necessário para permitir o drop (o padrão é negar)
        columnElement.addEventListener('dragover', function(e) {
            e.preventDefault(); // Essencial para permitir o drop
            e.dataTransfer.dropEffect = 'move';
            this.classList.add('drag-over'); // Feedback visual
        });

        // 'dragleave' para remover o feedback visual se sair da área
        columnElement.addEventListener('dragleave', function() {
            this.classList.remove('drag-over');
        });

        // 'drop' é onde a mágica acontece
        columnElement.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');

            const taskId = Number(e.dataTransfer.getData('text/plain'));
            const newStatus = statusKey; // 'todo', 'doing' ou 'done' dependendo da coluna

            // Se temos o card arrastado e ele mudou de coluna
            if (draggedItem && taskId) {
                // 1. Chama a API para salvar no banco
                updateTaskStatus(taskId, newStatus);
                
                // 2. Atualiza visualmente o card imediatamente (sem esperar o fetch)
                // Remove classes de status antigas
                draggedItem.classList.remove('todo', 'doing', 'done');
                // Adiciona a nova
                draggedItem.classList.add(newStatus);
                
                // Move o elemento HTML para a nova coluna
                this.appendChild(draggedItem);

                // Nota: Os botões de avançar/voltar ficarão "errados" até o próximo refresh 
                // se movermos via DOM. Para corrigir isso perfeitamente, teríamos que 
                // re-renderizar o card. Uma solução rápida é forçar um fetchTasks() após um breve delay.
                setTimeout(fetchTasks, 100);
            }
        });
    });


    /* =======================
       Renderização (Atualizada para Pedidos 2 e 3)
    ======================= */

    function renderCard(task) {
        const card = document.createElement("div");
        // Adicionamos o ID no dataset para o Drag & Drop encontrar fácil
        card.dataset.id = task.id; 
        card.classList.add("card", task.status);
        
        // Configura os eventos de arrastar neste card
        setupDraggableCard(card);

        const title = document.createElement("h4");
        title.textContent = task.title;
        const description = document.createElement("p");
        description.textContent = task.description || "";
        
        const actions = document.createElement("div");
        actions.classList.add("card-actions");

        // Calcula status adjacentes
        const { prev, next } = getAdjacentStatus(task.status);

        // --- Botão Voltar (←) --- (Pedido 2 e correção da observação)
        if (prev) {
            const prevBtn = document.createElement("button");
            prevBtn.innerHTML = "&larr;"; // Seta Esquerda HTML
            prevBtn.title = `Voltar para ${prev}`;
            prevBtn.classList.add("btn-action", "btn-move");
            prevBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                updateTaskStatus(task.id, prev);
            });
            actions.appendChild(prevBtn);
        }

        // --- Botão Avançar (→) ---
        if (next) {
            const nextBtn = document.createElement("button");
            nextBtn.innerHTML = "&rarr;"; // Seta Direita HTML
            nextBtn.title = `Avançar para ${next}`;
            nextBtn.classList.add("btn-action", "btn-move");
            nextBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                updateTaskStatus(task.id, next);
            });
            actions.appendChild(nextBtn);
        }

        // --- Botão Excluir (×) ---
        const deleteBtn = document.createElement("button");
        deleteBtn.innerHTML = "&times;";
        deleteBtn.title = "Excluir";
        deleteBtn.classList.add("btn-action", "btn-delete");
        deleteBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            deleteTask(task.id);
        });
        actions.appendChild(deleteBtn);

        card.appendChild(title);
        card.appendChild(description);
        card.appendChild(actions);

        return card;
    }

    // Inicialização
    taskForm.addEventListener("submit", addTask);
    fetchTasks();
});