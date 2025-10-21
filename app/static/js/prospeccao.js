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

        const response = await fetch(`${API_URL}/prospeccao/dados-linhas`, { headers: getHeaders() });

        if (response.status === 401) {
            logout();
            return;
        }

        const dadosLinhas = await response.json();
        let filteredData = dadosLinhas;

        if (busca) {
            filteredData = dadosLinhas.filter(item =>
                (item.numero_proposta && String(item.numero_proposta).toLowerCase().includes(busca.toLowerCase())) ||
                (item.empresa && String(item.empresa).toLowerCase().includes(busca.toLowerCase())) ||
                (item.cnpj && String(item.cnpj).toLowerCase().includes(busca.toLowerCase()))
            );
        }

        const tbody = document.getElementById('propostasTable');

        if (filteredData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-chart-line"></i></div>
                        <div class="empty-state-title">Nenhuma empresa em prospecção encontrada</div>
                        <div class="empty-state-description">Os dados das linhas educacional e tecnológica aparecerão aqui</div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = filteredData.map(item => {
            const consultor = item.consultor || '-';
            const programa = item.programa || item.tipo_programa || item.tipo || '-';
            const solucao = item.solucao ? item.solucao.substring(0, 50) + '...' : '-';

            return `
                <tr>
                    <td>${item.numero_proposta || '-'}</td>
                    <td>
                        <div style="font-weight: 600;">${item.empresa}</div>
                        <div style="font-size: 11px; color: var(--text-secondary);">${item.cnpj || ''}</div>
                    </td>
                    <td>${consultor}</td>
                    <td>
                        <div>${programa}</div>
                        <div style="font-size: 11px; color: var(--text-secondary);">
                            <span class="badge" style="background: ${item.linha === 'Educacional' ? '#10b981' : '#3b82f6'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px;">
                                ${item.linha}
                            </span>
                        </div>
                    </td>
                    <td>${item.valor ? 'R$ ' + item.valor.toLocaleString('pt-BR', {minimumFractionDigits: 2}) : '-'}</td>
                    <td>
                        <span class="badge" style="background: #6366f1; color: white; padding: 4px 12px; border-radius: 4px;">
                            ${item.status || item.situacao || 'N/A'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm" onclick="verDetalhes('${item.id}')" title="Ver Detalhes" style="background: #6366f1; color: white; padding: 6px 12px; border-radius: 4px; border: none; cursor: pointer;">
                            <i class="fas fa-eye"></i>
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

function verDetalhes(id) {
    alert('Visualizando detalhes do item: ' + id);
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
    
    const buscaProposta = document.getElementById('buscaProposta');
    if (buscaProposta) {
        buscaProposta.addEventListener('input', carregarPropostas);
    }
});
