const API_URL = '/api';

const darkLayout = {
    paper_bgcolor: '#1a1f3a',
    plot_bgcolor: '#151a30',
    font: { color: '#e4e6eb' },
    xaxis: { 
        gridcolor: '#2d3451',
        color: '#e4e6eb'
    },
    yaxis: { 
        gridcolor: '#2d3451',
        color: '#e4e6eb'
    }
};

const darkConfig = {
    displayModeBar: false,
    responsive: true
};

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

async function carregarDashboard() {
    try {
        const response = await fetch(`${API_URL}/bi/dashboard/`, {
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
            fetch(`${API_URL}/bi/propostas-por-status/`, { headers: getHeaders() }).then(r => r.json()),
            fetch(`${API_URL}/bi/receita-mensal/`, { headers: getHeaders() }).then(r => r.json()),
            fetch(`${API_URL}/bi/propostas-por-consultor/`, { headers: getHeaders() }).then(r => r.json()),
            fetch(`${API_URL}/bi/produtividade-consultores/`, { headers: getHeaders() }).then(r => r.json())
        ]);
        
        // Gráfico de Propostas por Status (Pizza)
        Plotly.newPlot('graficoPropostaStatus', [{
            values: propostaStatus.map(p => p.total),
            labels: propostaStatus.map(p => p.status),
            type: 'pie',
            marker: { 
                colors: ['#3b82f6', '#10b981', '#ef4444', '#f59e0b']
            },
            textfont: { color: '#e4e6eb' },
            hoverinfo: 'label+percent+value'
        }], {
            ...darkLayout,
            height: 300,
            margin: { t: 20, b: 20, l: 20, r: 20 },
            showlegend: true,
            legend: { 
                font: { color: '#e4e6eb' },
                bgcolor: 'transparent'
            }
        }, darkConfig);
        
        // Gráfico de Receita Mensal
        Plotly.newPlot('graficoReceitaMensal', [{
            x: receitaMensal.map(r => r.mes),
            y: receitaMensal.map(r => r.receita),
            type: 'bar',
            marker: { 
                color: '#3b82f6',
                line: { color: '#2563eb', width: 1 }
            },
            hovertemplate: 'R$ %{y:,.2f}<extra></extra>'
        }], {
            ...darkLayout,
            height: 300,
            margin: { t: 20, b: 40, l: 60, r: 20 },
            xaxis: { ...darkLayout.xaxis, tickangle: -45 },
            yaxis: { ...darkLayout.yaxis, tickprefix: 'R$ ' }
        }, darkConfig);
        
        // Gráfico de Propostas por Consultor
        Plotly.newPlot('graficoConsultor', [{
            x: consultores.map(c => c.consultor),
            y: consultores.map(c => c.total),
            type: 'bar',
            marker: { 
                color: '#10b981',
                line: { color: '#059669', width: 1 }
            },
            hovertemplate: '%{y} propostas<extra></extra>'
        }], {
            ...darkLayout,
            height: 300,
            margin: { t: 20, b: 80, l: 40, r: 20 },
            xaxis: { ...darkLayout.xaxis, tickangle: -45 }
        }, darkConfig);
        
        // Gráfico de Produtividade (Horas)
        Plotly.newPlot('graficoProdutividade', [{
            x: produtividade.map(p => p.consultor),
            y: produtividade.map(p => p.horas),
            type: 'bar',
            marker: { 
                color: '#f59e0b',
                line: { color: '#d97706', width: 1 }
            },
            hovertemplate: '%{y} horas<extra></extra>'
        }], {
            ...darkLayout,
            height: 300,
            margin: { t: 20, b: 80, l: 40, r: 20 },
            xaxis: { ...darkLayout.xaxis, tickangle: -45 },
            yaxis: { ...darkLayout.yaxis, title: 'Horas' }
        }, darkConfig);
    } catch (error) {
        console.error('Erro ao carregar gráficos:', error);
    }
}

async function enviarPergunta() {
    const input = document.getElementById('chatInput');
    const responseDiv = document.getElementById('chatResponse');
    const pergunta = input.value.trim();
    
    if (!pergunta) return;
    
    responseDiv.style.display = 'block';
    responseDiv.innerHTML = '<div style="display: flex; align-items: center; gap: 12px;"><span class="loading-spinner"></span><span>Processando...</span></div>';
    
    try {
        const response = await fetch(`${API_URL}/chatbot/perguntar/`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ pergunta })
        });
        
        if (!response.ok) {
            throw new Error('Erro na resposta');
        }
        
        const data = await response.json();
        
        let html = `<div style="color: var(--text-primary);"><strong>Resposta:</strong><br>${data.resposta}</div>`;
        
        if (data.dados) {
            if (data.dados.contratos && data.dados.contratos.length > 0) {
                html += '<ul style="margin-top: 12px; color: var(--text-secondary);">';
                data.dados.contratos.forEach(c => {
                    html += `<li>${c.numero} - ${c.empresa} - Vencimento: ${c.vencimento} - R$ ${parseFloat(c.valor).toFixed(2)}</li>`;
                });
                html += '</ul>';
            }
            
            if (data.dados.projetos && data.dados.projetos.length > 0) {
                html += '<ul style="margin-top: 12px; color: var(--text-secondary);">';
                data.dados.projetos.forEach(p => {
                    html += `<li>${p.numero_proposta} - ${p.empresa} - ${p.percentual}% concluído</li>`;
                });
                html += '</ul>';
            }
        }
        
        responseDiv.innerHTML = html;
        input.value = '';
    } catch (error) {
        console.error('Erro:', error);
        responseDiv.innerHTML = '<div style="color: var(--accent-danger);">Erro ao processar pergunta. Tente novamente.</div>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const token = getToken();
    if (!token) {
        window.location.href = '/';
        return;
    }
    
    carregarDashboard();
    
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                enviarPergunta();
            }
        });
    }
});
