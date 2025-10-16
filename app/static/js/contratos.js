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
    window.location.href = '/';
}

async function carregarContratos() {
    try {
        const response = await fetch(`${API_URL}/contratos?limit=100`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const contratos = await response.json();
        const tbody = document.getElementById('tabelaContratos');
        
        tbody.innerHTML = contratos.map(c => `
            <tr>
                <td>${c.numero_contrato}</td>
                <td>ID: ${c.proposta_id}</td>
                <td>${c.data_assinatura || '-'}</td>
                <td>${c.data_vencimento || '-'}</td>
                <td>R$ ${(c.valor || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                <td><span class="badge bg-${c.status_pagamento === 'Pago' ? 'success' : c.status_pagamento === 'Vencido' ? 'danger' : 'warning'}">${c.status_pagamento}</span></td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deletarContrato(${c.id})">Excluir</button>
                </td>
            </tr>
        `).join('');
        
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
        
        const alertas = await response.json();
        const alertDiv = document.getElementById('alertasContratosVencidos');
        
        if (alertas.length > 0) {
            alertDiv.innerHTML = `<strong>Atenção!</strong> ${alertas.length} contrato(s) com vencimento próximo ou vencido.`;
            alertDiv.style.display = 'block';
        } else {
            alertDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Erro ao verificar contratos:', error);
    }
}

async function salvarContrato() {
    const contrato = {
        numero_contrato: document.getElementById('numero_contrato').value,
        proposta_id: parseInt(document.getElementById('proposta_id').value),
        data_assinatura: document.getElementById('data_assinatura').value || null,
        data_vencimento: document.getElementById('data_vencimento').value || null,
        valor: parseFloat(document.getElementById('valor').value) || null,
        status_pagamento: document.getElementById('status_pagamento').value
    };
    
    try {
        const response = await fetch(`${API_URL}/contratos`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(contrato)
        });
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('modalContrato')).hide();
            carregarContratos();
            document.getElementById('formContrato').reset();
        } else {
            alert('Erro ao salvar contrato');
        }
    } catch (error) {
        console.error('Erro ao salvar contrato:', error);
    }
}

async function deletarContrato(id) {
    if (!confirm('Deseja realmente excluir este contrato?')) return;
    
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
        console.error('Erro ao excluir contrato:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!getToken()) {
        window.location.href = '/';
        return;
    }
    
    carregarContratos();
});
