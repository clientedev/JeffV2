const API_URL = '/api';

function getToken() {
    return localStorage.getItem('token');
}

function getHeaders() {
    return {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
    };
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

async function carregarCronogramas() {
    try {
        const response = await fetch(`${API_URL}/cronogramas/?limit=100`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const cronogramas = await response.json();
        const tbody = document.getElementById('cronogramasTable');
        
        if (cronogramas.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-calendar-alt"></i></div>
                        <div class="empty-state-title">Nenhum cronograma encontrado</div>
                        <div class="empty-state-description">Comece adicionando um novo cronograma</div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = cronogramas.map(c => {
            let statusClass = 'badge-primary';
            if (c.status === 'Concluído') statusClass = 'badge-success';
            else if (c.status === 'Atrasado') statusClass = 'badge-danger';
            else if (c.status === 'Em andamento') statusClass = 'badge-info';
            
            return `
                <tr>
                    <td>${c.proposta ? (c.proposta.numero_proposta || 'ID: ' + c.proposta_id) : 'ID: ' + c.proposta_id}</td>
                    <td>${c.data_inicio ? new Date(c.data_inicio).toLocaleDateString('pt-BR') : '-'}</td>
                    <td>${c.data_termino ? new Date(c.data_termino).toLocaleDateString('pt-BR') : '-'}</td>
                    <td>${c.horas_previstas || 0}h</td>
                    <td>${c.horas_executadas || 0}h</td>
                    <td>${c.percentual_conclusao || 0}%</td>
                    <td><span class="badge ${statusClass}">${c.status || 'Não iniciado'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editarCronograma(${c.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deletarCronograma(${c.id})" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
        
        verificarAlertas();
    } catch (error) {
        console.error('Erro ao carregar cronogramas:', error);
    }
}

async function verificarAlertas() {
    try {
        const response = await fetch(`${API_URL}/cronogramas/alertas`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const alertas = await response.json();
            const alertDiv = document.getElementById('alertasVencimento');
            
            if (alertas.length > 0) {
                alertDiv.innerHTML = `
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Atenção!</strong> ${alertas.length} cronograma(s) com vencimento próximo ou atrasado.
                `;
                alertDiv.style.display = 'block';
            } else {
                alertDiv.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Erro ao verificar alertas:', error);
    }
}

async function deletarCronograma(id) {
    if (!confirm('Tem certeza que deseja excluir este cronograma?')) return;
    
    try {
        const response = await fetch(`${API_URL}/cronogramas/${id}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.ok) {
            carregarCronogramas();
        } else {
            alert('Erro ao excluir cronograma');
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao excluir cronograma');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const token = getToken();
    if (!token) {
        window.location.href = '/';
        return;
    }
    
    carregarCronogramas();
});
