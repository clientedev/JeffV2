let stages = [];
let companies = [];
let currentCompanyId = null;

async function loadStages() {
    const response = await fetch('/api/pipeline/stages', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    stages = await response.json();
    
    const stageSelect = document.getElementById('newStageId');
    stageSelect.innerHTML = stages.map(s => 
        `<option value="${s.id}">${s.nome}</option>`
    ).join('');
    
    renderKanbanBoard();
}

async function loadCompanies() {
    const linha = document.getElementById('filterLinha').value;
    const consultor = document.getElementById('filterConsultor').value;
    
    let url = '/api/pipeline/companies?';
    if (linha) url += `linha=${linha}&`;
    if (consultor) url += `consultor=${consultor}&`;
    
    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    companies = await response.json();
    renderKanbanBoard();
}

function renderKanbanBoard() {
    const board = document.getElementById('kanbanBoard');
    board.innerHTML = '';
    
    stages.forEach(stage => {
        const stageCompanies = companies.filter(c => c.stage_id === stage.id);
        
        const column = document.createElement('div');
        column.className = 'kanban-column';
        column.dataset.stageId = stage.id;
        
        column.innerHTML = `
            <div class="kanban-column-header" style="border-color: ${stage.cor};">
                <div class="kanban-column-title" style="color: ${stage.cor};">${stage.nome}</div>
                <div class="kanban-column-count" style="color: ${stage.cor};">${stageCompanies.length}</div>
            </div>
            <div class="kanban-cards" data-stage-id="${stage.id}">
                ${stageCompanies.map(company => createCompanyCard(company, stage.cor)).join('')}
            </div>
        `;
        
        board.appendChild(column);
        
        const cardsContainer = column.querySelector('.kanban-cards');
        setupDragAndDrop(cardsContainer);
    });
}

function createCompanyCard(company, color) {
    const warning = company.dias_na_etapa > 7 ? 
        `<div class="kanban-card-warning">⚠️ Parada há ${company.dias_na_etapa} dias</div>` : '';
    
    return `
        <div class="kanban-card" draggable="true" data-company-id="${company.id}" 
             style="border-color: ${color};" onclick="openCompanyDetails(${company.id})">
            <div class="kanban-card-title">${company.nome_empresa}</div>
            <div class="kanban-card-meta">
                <span class="kanban-card-badge">${company.linha}</span>
                ${company.consultor_responsavel ? `<span class="kanban-card-badge">${company.consultor_responsavel}</span>` : ''}
                ${company.valor_proposta ? `<span class="kanban-card-badge">R$ ${formatCurrency(company.valor_proposta)}</span>` : ''}
            </div>
            ${warning}
        </div>
    `;
}

function setupDragAndDrop(container) {
    container.addEventListener('dragover', e => {
        e.preventDefault();
        const afterElement = getDragAfterElement(container, e.clientY);
        const dragging = document.querySelector('.dragging');
        if (afterElement == null) {
            container.appendChild(dragging);
        } else {
            container.insertBefore(dragging, afterElement);
        }
    });
    
    container.addEventListener('drop', async e => {
        e.preventDefault();
        const dragging = document.querySelector('.dragging');
        if (!dragging) return;
        
        const companyId = dragging.dataset.companyId;
        const newStageId = parseInt(container.dataset.stageId);
        
        await moveCompanyToStage(companyId, newStageId);
    });
    
    const cards = container.querySelectorAll('.kanban-card');
    cards.forEach(card => {
        card.addEventListener('dragstart', () => {
            card.classList.add('dragging');
        });
        
        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
        });
    });
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.kanban-card:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

async function moveCompanyToStage(companyId, newStageId) {
    try {
        const response = await fetch(`/api/pipeline/companies/${companyId}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                stage_id: newStageId,
                observacao: 'Movido via Kanban'
            })
        });
        
        if (response.ok) {
            showNotification('Empresa movida com sucesso!', 'success');
            await loadCompanies();
        } else {
            showNotification('Erro ao mover empresa', 'error');
        }
    } catch (error) {
        showNotification('Erro ao mover empresa', 'error');
    }
}

async function openCompanyDetails(companyId) {
    currentCompanyId = companyId;
    const company = companies.find(c => c.id === companyId);
    
    document.getElementById('modalTitle').textContent = company.nome_empresa;
    
    const detailsContent = document.getElementById('companyDetailsContent');
    detailsContent.innerHTML = `
        <div class="company-details">
            <div class="detail-item">
                <div class="detail-label">CNPJ</div>
                <div class="detail-value">${company.cnpj}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Linha</div>
                <div class="detail-value">${company.linha}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Tipo de Programa</div>
                <div class="detail-value">${company.tipo_programa || '-'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Porte</div>
                <div class="detail-value">${company.porte || '-'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">ER / Região</div>
                <div class="detail-value">${company.er_regiao || '-'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Consultor</div>
                <div class="detail-value">${company.consultor_responsavel || '-'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Etapa Atual</div>
                <div class="detail-value" style="color: ${company.stage.cor};">${company.stage.nome}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Dias na Etapa</div>
                <div class="detail-value">${company.dias_na_etapa} dias</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Nº Proposta</div>
                <div class="detail-value">${company.numero_proposta || '-'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Valor Proposta</div>
                <div class="detail-value">${company.valor_proposta ? 'R$ ' + formatCurrency(company.valor_proposta) : '-'}</div>
            </div>
        </div>
        ${company.observacoes ? `
            <div style="margin-top: 20px; padding: 12px; background: #f9fafb; border-radius: 6px;">
                <div class="detail-label">Observações</div>
                <div style="margin-top: 8px;">${company.observacoes}</div>
            </div>
        ` : ''}
    `;
    
    await loadHistory(companyId);
    await loadNotes(companyId);
    
    document.getElementById('companyModal').classList.add('active');
}

async function loadHistory(companyId) {
    const response = await fetch(`/api/pipeline/companies/${companyId}/history`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const history = await response.json();
    
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = history.map(h => `
        <div class="timeline-item">
            <div style="font-weight: 600; color: ${h.stage.cor};">${h.stage.nome}</div>
            <div style="font-size: 12px; color: #6b7280; margin: 4px 0;">
                ${formatDateTime(h.data_entrada)} 
                ${h.data_saida ? '→ ' + formatDateTime(h.data_saida) : '(Atual)'}
            </div>
            <div style="font-size: 12px; color: #6b7280;">
                ${h.dias_na_etapa} dias nesta etapa
            </div>
            ${h.usuario ? `<div style="font-size: 12px; color: #6b7280;">Por: ${h.usuario}</div>` : ''}
            ${h.observacao ? `<div style="margin-top: 8px; font-size: 13px;">${h.observacao}</div>` : ''}
        </div>
    `).join('');
}

async function loadNotes(companyId) {
    const response = await fetch(`/api/pipeline/companies/${companyId}/notes`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    const notes = await response.json();
    
    const notesContent = document.getElementById('notesContent');
    notesContent.innerHTML = notes.map(n => `
        <div class="note-item">
            ${n.titulo ? `<div style="font-weight: 600; margin-bottom: 4px;">${n.titulo}</div>` : ''}
            <div style="margin-bottom: 8px;">${n.conteudo}</div>
            <div style="font-size: 11px; color: #6b7280;">
                ${n.usuario_nome} - ${formatDateTime(n.criado_em)}
                ${n.privada ? '<span style="color: #dc2626;"> (Privada)</span>' : ''}
            </div>
        </div>
    `).join('');
}

async function addNote() {
    const content = document.getElementById('newNoteContent').value;
    if (!content) return;
    
    const response = await fetch(`/api/pipeline/companies/${currentCompanyId}/notes`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
            conteudo: content,
            privada: false
        })
    });
    
    if (response.ok) {
        document.getElementById('newNoteContent').value = '';
        await loadNotes(currentCompanyId);
        showNotification('Nota adicionada com sucesso!', 'success');
    }
}

function closeCompanyModal() {
    document.getElementById('companyModal').classList.remove('active');
}

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

function openAddCompanyModal() {
    document.getElementById('addCompanyModal').classList.add('active');
}

function closeAddCompanyModal() {
    document.getElementById('addCompanyModal').classList.remove('active');
}

async function submitNewCompany(event) {
    event.preventDefault();
    
    const data = {
        cnpj: document.getElementById('newCnpj').value,
        nome_empresa: document.getElementById('newNomeEmpresa').value,
        linha: document.getElementById('newLinha').value,
        tipo_programa: document.getElementById('newTipoPrograma').value,
        porte: document.getElementById('newPorte').value,
        er_regiao: document.getElementById('newErRegiao').value,
        consultor_responsavel: document.getElementById('newConsultor').value,
        stage_id: parseInt(document.getElementById('newStageId').value),
        numero_proposta: document.getElementById('newNumeroProposta').value,
        valor_proposta: parseFloat(document.getElementById('newValorProposta').value) || null,
        observacoes: document.getElementById('newObservacoes').value
    };
    
    const response = await fetch('/api/pipeline/companies', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(data)
    });
    
    if (response.ok) {
        showNotification('Empresa cadastrada com sucesso!', 'success');
        closeAddCompanyModal();
        document.getElementById('addCompanyForm').reset();
        await loadCompanies();
    } else {
        const error = await response.json();
        showNotification(error.detail || 'Erro ao cadastrar empresa', 'error');
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function openImportModal() {
    document.getElementById('importModal').classList.add('active');
}

function closeImportModal() {
    document.getElementById('importModal').classList.remove('active');
    document.getElementById('importProgress').style.display = 'none';
}

async function importarDados() {
    const linha = document.getElementById('importLinha').value;

    if (!linha) {
        showNotification('Por favor, selecione uma linha', 'error');
        return;
    }

    document.getElementById('importProgress').style.display = 'block';

    try {
        const response = await fetch('/api/pipeline/importar-de-linhas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({ linha })
        });

        const result = await response.json();

        if (response.ok) {
            showNotification(`Importação concluída! ${result.importados} empresas importadas.`, 'success');

            if (result.erros && result.erros.length > 0) {
                console.warn('Erros durante importação:', result.erros);
            }

            closeImportModal();
            await loadCompanies();
        } else {
            showNotification(result.detail || 'Erro ao importar dados', 'error');
        }
    } catch (error) {
        console.error('Erro ao importar:', error);
        showNotification('Erro ao importar dados das linhas', 'error');
    } finally {
        document.getElementById('importProgress').style.display = 'none';
    }
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 6px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

document.getElementById('filterLinha').addEventListener('change', loadCompanies);
document.getElementById('filterConsultor').addEventListener('input', debounce(loadCompanies, 500));

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

document.addEventListener('DOMContentLoaded', async () => {
    await loadStages();
    await loadCompanies();
});
