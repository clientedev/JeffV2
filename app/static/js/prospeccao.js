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

async function carregarPropostas() {
    try {
        const status = document.getElementById('filtroStatus').value;
        const busca = document.getElementById('buscaProposta').value;
        
        let url = `${API_URL}/propostas?limit=100`;
        if (status) url += `&status_filter=${status}`;
        
        const response = await fetch(url, { headers: getHeaders() });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const propostas = await response.json();
        let filteredPropostas = propostas;
        
        if (busca) {
            filteredPropostas = propostas.filter(p => 
                (p.numero_proposta && p.numero_proposta.toLowerCase().includes(busca.toLowerCase())) ||
                (p.empresa && p.empresa.nome && p.empresa.nome.toLowerCase().includes(busca.toLowerCase()))
            );
        }
        
        const tbody = document.getElementById('propostasTable');
        
        if (filteredPropostas.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="empty-state-title">Nenhuma proposta encontrada</div>
                        <div class="empty-state-description">Comece adicionando uma nova proposta</div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = filteredPropostas.map(p => {
            let statusClass = 'badge-primary';
            if (p.status === 'Fechado') statusClass = 'badge-success';
            else if (p.status === 'Perdido') statusClass = 'badge-danger';
            
            return `
                <tr>
                    <td>${p.numero_proposta || '-'}</td>
                    <td>${p.empresa ? p.empresa.nome : 'ID: ' + p.empresa_id}</td>
                    <td>${p.consultor ? p.consultor.nome : (p.consultor_id ? 'ID: ' + p.consultor_id : 'N/A')}</td>
                    <td>${p.solucao || '-'}</td>
                    <td>R$ ${(p.valor_proposta || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td><span class="badge ${statusClass}">${p.status || 'Em andamento'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editarProposta(${p.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deletarProposta(${p.id})" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Erro ao carregar propostas:', error);
    }
}

async function carregarEmpresas() {
    try {
        const response = await fetch(`${API_URL}/empresas?limit=1000`, { headers: getHeaders() });
        const empresas = await response.json();
        
        const select = document.getElementById('empresa_id');
        if (select) {
            select.innerHTML = '<option value="">Selecione...</option>' + 
                empresas.map(e => `<option value="${e.id}">${e.nome}</option>`).join('');
        }
    } catch (error) {
        console.error('Erro ao carregar empresas:', error);
    }
}

async function carregarConsultores() {
    try {
        const response = await fetch(`${API_URL}/consultores?limit=1000`, { headers: getHeaders() });
        const consultores = await response.json();
        
        const select = document.getElementById('consultor_id');
        if (select) {
            select.innerHTML = '<option value="">Selecione...</option>' + 
                consultores.map(c => `<option value="${c.id}">${c.nome}</option>`).join('');
        }
    } catch (error) {
        console.error('Erro ao carregar consultores:', error);
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
    
    if (!proposta.numero_proposta || !proposta.empresa_id) {
        alert('Preencha os campos obrigatórios');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/propostas`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(proposta)
        });
        
        if (response.ok) {
            fecharModal();
            carregarPropostas();
            document.getElementById('formProposta').reset();
        } else {
            const error = await response.json();
            alert('Erro ao salvar proposta: ' + (error.detail || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao salvar proposta');
    }
}

async function deletarProposta(id) {
    if (!confirm('Tem certeza que deseja excluir esta proposta?')) return;
    
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
        console.error('Erro:', error);
        alert('Erro ao excluir proposta');
    }
}

function fecharModal() {
    document.getElementById('modalProposta').classList.remove('active');
}

document.addEventListener('DOMContentLoaded', () => {
    const token = getToken();
    if (!token) {
        window.location.href = '/';
        return;
    }
    
    carregarPropostas();
    carregarEmpresas();
    carregarConsultores();
    
    const filtroStatus = document.getElementById('filtroStatus');
    const buscaProposta = document.getElementById('buscaProposta');
    
    if (filtroStatus) {
        filtroStatus.addEventListener('change', carregarPropostas);
    }
    
    if (buscaProposta) {
        buscaProposta.addEventListener('input', carregarPropostas);
    }
});
