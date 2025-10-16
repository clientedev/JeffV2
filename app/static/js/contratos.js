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

async function carregarContratos() {
    try {
        const response = await fetch(`${API_URL}/contratos/?limit=100`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const contratos = await response.json();
        const tbody = document.getElementById('contratosTable');
        
        if (contratos.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-file-contract"></i></div>
                        <div class="empty-state-title">Nenhum contrato encontrado</div>
                        <div class="empty-state-description">Comece adicionando um novo contrato</div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = contratos.map(c => {
            let statusClass = 'badge-warning';
            if (c.status_pagamento === 'Pago') statusClass = 'badge-success';
            else if (c.status_pagamento === 'Vencido') statusClass = 'badge-danger';
            else if (c.status_pagamento === 'Cancelado') statusClass = 'badge-secondary';
            
            return `
                <tr>
                    <td>${c.numero_contrato || '-'}</td>
                    <td>${c.proposta ? (c.proposta.numero_proposta || 'ID: ' + c.proposta_id) : 'ID: ' + c.proposta_id}</td>
                    <td>${c.data_assinatura ? new Date(c.data_assinatura).toLocaleDateString('pt-BR') : '-'}</td>
                    <td>${c.data_vencimento ? new Date(c.data_vencimento).toLocaleDateString('pt-BR') : '-'}</td>
                    <td>R$ ${(c.valor || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td><span class="badge ${statusClass}">${c.status_pagamento || 'Pendente'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editarContrato(${c.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deletarContrato(${c.id})" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
        
        verificarContratosVencidos();
    } catch (error) {
        console.error('Erro ao carregar contratos:', error);
    }
}

async function verificarContratosVencidos() {
    try {
        const response = await fetch(`${API_URL}/contratos/alertas`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const alertas = await response.json();
            const alertDiv = document.getElementById('alertasContratosVencidos');
            
            if (alertas.length > 0) {
                alertDiv.innerHTML = `
                    <i class="fas fa-exclamation-circle"></i>
                    <strong>Atenção!</strong> ${alertas.length} contrato(s) com vencimento próximo ou vencido.
                `;
                alertDiv.style.display = 'block';
            } else {
                alertDiv.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Erro ao verificar contratos:', error);
    }
}

async function deletarContrato(id) {
    if (!confirm('Tem certeza que deseja excluir este contrato?')) return;
    
    try {
        const response = await fetch(`${API_URL}/contratos/${id}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.ok) {
            carregarContratos();
        } else {
            alert('Erro ao excluir contrato');
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao excluir contrato');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const token = getToken();
    if (!token) {
        window.location.href = '/';
        return;
    }
    
    carregarContratos();
});
