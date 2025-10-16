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

async function carregarDashboard() {
    try {
        const response = await fetch(`${API_URL}/bi/dashboard`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const data = await response.json();
        
        document.getElementById('propostas_ativas').textContent = data.propostas_ativas || 0;
        document.getElementById('propostas_fechadas_mes').textContent = data.propostas_fechadas_mes || 0;
        document.getElementById('taxa_conversao').textContent = `${data.taxa_conversao || 0}%`;
        document.getElementById('receita_mes').textContent = `R$ ${(data.receita_mes || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        
        carregarGraficos();
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
    }
}

async function carregarGraficos() {
    try {
        const [propostaStatus, receitaMensal, consultores, produtividade] = await Promise.all([
            fetch(`${API_URL}/bi/propostas-por-status`, { headers: getHeaders() }).then(r => r.json()),
            fetch(`${API_URL}/bi/receita-mensal`, { headers: getHeaders() }).then(r => r.json()),
            fetch(`${API_URL}/bi/propostas-por-consultor`, { headers: getHeaders() }).then(r => r.json()),
            fetch(`${API_URL}/bi/produtividade-consultores`, { headers: getHeaders() }).then(r => r.json())
        ]);
        
        Plotly.newPlot('graficoPropostaStatus', [{
            values: propostaStatus.map(p => p.total),
            labels: propostaStatus.map(p => p.status),
            type: 'pie',
            marker: { colors: ['#0d6efd', '#198754', '#dc3545'] }
        }], {
            height: 300,
            margin: { t: 20, b: 20, l: 20, r: 20 }
        });
        
        Plotly.newPlot('graficoReceitaMensal', [{
            x: receitaMensal.map(r => r.mes),
            y: receitaMensal.map(r => r.receita),
            type: 'bar',
            marker: { color: '#ffc107' }
        }], {
            height: 300,
            margin: { t: 20, b: 40, l: 60, r: 20 }
        });
        
        Plotly.newPlot('graficoConsultor', [{
            x: consultores.map(c => c.consultor),
            y: consultores.map(c => c.total),
            type: 'bar',
            marker: { color: '#0dcaf0' }
        }], {
            height: 300,
            margin: { t: 20, b: 60, l: 40, r: 20 }
        });
        
        Plotly.newPlot('graficoProdutividade', [{
            x: produtividade.map(p => p.consultor),
            y: produtividade.map(p => p.horas),
            type: 'bar',
            marker: { color: '#198754' }
        }], {
            height: 300,
            margin: { t: 20, b: 60, l: 40, r: 20 }
        });
    } catch (error) {
        console.error('Erro ao carregar gráficos:', error);
    }
}

async function enviarPergunta() {
    const input = document.getElementById('chatInput');
    const responseDiv = document.getElementById('chatResponse');
    const mensagem = input.value.trim();
    
    if (!mensagem) return;
    
    responseDiv.innerHTML = '<div class="loading"></div> Processando...';
    
    try {
        const response = await fetch(`${API_URL}/chatbot/perguntar`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ mensagem })
        });
        
        const data = await response.json();
        
        let html = `<p><strong>Resposta:</strong> ${data.resposta}</p>`;
        
        if (data.dados.contratos && data.dados.contratos.length > 0) {
            html += '<ul>';
            data.dados.contratos.forEach(c => {
                html += `<li>${c.numero} - ${c.empresa} - Vencimento: ${c.vencimento} - R$ ${c.valor.toFixed(2)}</li>`;
            });
            html += '</ul>';
        }
        
        if (data.dados.projetos && data.dados.projetos.length > 0) {
            html += '<ul>';
            data.dados.projetos.forEach(p => {
                html += `<li>${p.numero_proposta} - ${p.empresa} - ${p.percentual}% concluído</li>`;
            });
            html += '</ul>';
        }
        
        responseDiv.innerHTML = html;
        input.value = '';
    } catch (error) {
        responseDiv.innerHTML = '<p class="text-danger">Erro ao processar pergunta</p>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!getToken()) {
        window.location.href = '/';
        return;
    }
    
    carregarDashboard();
    
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') enviarPergunta();
    });
});
