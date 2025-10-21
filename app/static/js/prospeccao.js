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
        const busca = document.getElementById('buscaProposta').value;
        
        const response = await fetch(`${API_URL}/prospeccao/pipeline`, { headers: getHeaders() });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const companies = await response.json();
        let filteredCompanies = companies;
        
        if (busca) {
            filteredCompanies = companies.filter(c => 
                (c.numero_proposta && c.numero_proposta.toLowerCase().includes(busca.toLowerCase())) ||
                (c.empresa && c.empresa.toLowerCase().includes(busca.toLowerCase())) ||
                (c.cnpj && c.cnpj.toLowerCase().includes(busca.toLowerCase()))
            );
        }
        
        const tbody = document.getElementById('propostasTable');
        
        if (filteredCompanies.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="empty-state-title">Nenhuma empresa em prospecção encontrada</div>
                        <div class="empty-state-description">As empresas em prospecção aparecerão aqui</div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = filteredCompanies.map(c => {
            return `
                <tr>
                    <td>${c.numero_proposta || '-'}</td>
                    <td>
                        <div style="font-weight: 600;">${c.empresa}</div>
                        <div style="font-size: 11px; color: var(--text-secondary);">${c.cnpj || ''}</div>
                    </td>
                    <td>${c.consultor || '-'}</td>
                    <td>
                        <div>${c.tipo_programa || '-'}</div>
                        <div style="font-size: 11px; color: var(--text-secondary);">${c.linha}</div>
                    </td>
                    <td>${c.valor_proposta ? 'R$ ' + c.valor_proposta.toLocaleString('pt-BR', {minimumFractionDigits: 2}) : '-'}</td>
                    <td><span class="badge badge-primary" style="background-color: ${c.stage_cor};">${c.stage || 'N/A'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="window.location.href='/pipeline'" title="Ver no Pipeline">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Erro ao carregar empresas:', error);
        document.getElementById('propostasTable').innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px; color: var(--text-danger);">
                    Erro ao carregar dados. Tente novamente.
                </td>
            </tr>
        `;
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
