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

async function carregarPropostas() {
    try {
        const status = document.getElementById('filtroStatus').value;
        let url = `${API_URL}/propostas?limit=100`;
        if (status) url += `&status_filter=${status}`;
        
        const response = await fetch(url, { headers: getHeaders() });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const propostas = await response.json();
        const tbody = document.getElementById('tabelaPropostas');
        
        tbody.innerHTML = propostas.map(p => `
            <tr>
                <td>${p.numero_proposta}</td>
                <td>ID: ${p.empresa_id}</td>
                <td>ID: ${p.consultor_id || 'N/A'}</td>
                <td>${p.solucao || '-'}</td>
                <td>R$ ${(p.valor_proposta || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                <td><span class="badge bg-${p.status === 'Fechado' ? 'success' : p.status === 'Perdido' ? 'danger' : 'primary'}">${p.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deletarProposta(${p.id})">Excluir</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar propostas:', error);
    }
}

async function salvarProposta() {
    const proposta = {
        numero_proposta: document.getElementById('numero_proposta').value,
        empresa_id: parseInt(document.getElementById('empresa_id').value),
        consultor_id: parseInt(document.getElementById('consultor_id').value) || null,
        solucao: document.getElementById('solucao').value,
        valor_proposta: parseFloat(document.getElementById('valor_proposta').value) || null,
        status: document.getElementById('status').value
    };
    
    try {
        const response = await fetch(`${API_URL}/propostas`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(proposta)
        });
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('modalProposta')).hide();
            carregarPropostas();
            document.getElementById('formProposta').reset();
        } else {
            alert('Erro ao salvar proposta');
        }
    } catch (error) {
        console.error('Erro ao salvar proposta:', error);
    }
}

async function deletarProposta(id) {
    if (!confirm('Deseja realmente excluir esta proposta?')) return;
    
    try {
        const response = await fetch(`${API_URL}/propostas/${id}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.ok) {
            carregarPropostas();
        } else {
            alert('Erro ao excluir proposta');
        }
    } catch (error) {
        console.error('Erro ao excluir proposta:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!getToken()) {
        window.location.href = '/';
        return;
    }
    
    carregarPropostas();
});
