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

async function carregarCronogramas() {
    try {
        const response = await fetch(`${API_URL}/cronogramas?limit=100`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const cronogramas = await response.json();
        const tbody = document.getElementById('tabelaCronogramas');
        
        tbody.innerHTML = cronogramas.map(c => `
            <tr>
                <td>ID: ${c.proposta_id}</td>
                <td>${c.data_inicio || '-'}</td>
                <td>${c.data_termino || '-'}</td>
                <td>${c.horas_previstas || 0}h</td>
                <td>${c.horas_executadas || 0}h</td>
                <td>${c.percentual_conclusao || 0}%</td>
                <td><span class="badge bg-${c.status === 'Concluído' ? 'success' : c.status === 'Atrasado' ? 'danger' : 'primary'}">${c.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deletarCronograma(${c.id})">Excluir</button>
                </td>
            </tr>
        `).join('');
        
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
        
        const alertas = await response.json();
        const alertDiv = document.getElementById('alertasVencimento');
        
        if (alertas.length > 0) {
            alertDiv.innerHTML = `<strong>Atenção!</strong> ${alertas.length} cronograma(s) com vencimento próximo ou atrasado.`;
            alertDiv.style.display = 'block';
        } else {
            alertDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Erro ao verificar alertas:', error);
    }
}

async function salvarCronograma() {
    const cronograma = {
        proposta_id: parseInt(document.getElementById('proposta_id').value),
        data_inicio: document.getElementById('data_inicio').value || null,
        data_termino: document.getElementById('data_termino').value || null,
        horas_previstas: parseFloat(document.getElementById('horas_previstas').value) || null,
        status: document.getElementById('status').value
    };
    
    try {
        const response = await fetch(`${API_URL}/cronogramas`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(cronograma)
        });
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('modalCronograma')).hide();
            carregarCronogramas();
            document.getElementById('formCronograma').reset();
        } else {
            alert('Erro ao salvar cronograma');
        }
    } catch (error) {
        console.error('Erro ao salvar cronograma:', error);
    }
}

async function deletarCronograma(id) {
    if (!confirm('Deseja realmente excluir este cronograma?')) return;
    
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
        console.error('Erro ao excluir cronograma:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!getToken()) {
        window.location.href = '/';
        return;
    }
    
    carregarCronogramas();
});
