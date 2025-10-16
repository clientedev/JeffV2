const API_URL = '/api';

function getToken() {
    return localStorage.getItem('token');
}

function getHeaders() {
    return {
        'Authorization': `Bearer ${getToken()}`
    };
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

async function importarEmpresas() {
    const fileInput = document.getElementById('fileEmpresas');
    const resultDiv = document.getElementById('resultEmpresas');
    
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Selecione um arquivo</div>';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    resultDiv.innerHTML = '<div class="loading"></div> Importando...';
    
    try {
        const response = await fetch(`${API_URL}/importacao/empresas/`, {
            method: 'POST',
            headers: getHeaders(),
            body: formData
        });
        
        const result = await response.json();
        
        if (result.sucesso) {
            let html = `<div class="alert alert-success">
                <strong>Sucesso!</strong> ${result.registros_importados} registro(s) importado(s).
            </div>`;
            
            if (result.erros.length > 0) {
                html += `<div class="alert alert-warning">
                    <strong>Avisos:</strong><br>${result.erros.slice(0, 5).join('<br>')}
                </div>`;
            }
            
            resultDiv.innerHTML = html;
            fileInput.value = '';
        } else {
            resultDiv.innerHTML = '<div class="alert alert-danger">Erro na importação</div>';
        }
    } catch (error) {
        resultDiv.innerHTML = '<div class="alert alert-danger">Erro ao processar arquivo</div>';
    }
}

async function importarPropostas() {
    const fileInput = document.getElementById('filePropostas');
    const resultDiv = document.getElementById('resultPropostas');
    
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Selecione um arquivo</div>';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    resultDiv.innerHTML = '<div class="loading"></div> Importando...';
    
    try {
        const response = await fetch(`${API_URL}/importacao/propostas/`, {
            method: 'POST',
            headers: getHeaders(),
            body: formData
        });
        
        const result = await response.json();
        
        if (result.sucesso) {
            let html = `<div class="alert alert-success">
                <strong>Sucesso!</strong> ${result.registros_importados} registro(s) importado(s).
            </div>`;
            
            if (result.erros.length > 0) {
                html += `<div class="alert alert-warning">
                    <strong>Avisos:</strong><br>${result.erros.slice(0, 5).join('<br>')}
                </div>`;
            }
            
            resultDiv.innerHTML = html;
            fileInput.value = '';
        } else {
            resultDiv.innerHTML = '<div class="alert alert-danger">Erro na importação</div>';
        }
    } catch (error) {
        resultDiv.innerHTML = '<div class="alert alert-danger">Erro ao processar arquivo</div>';
    }
}

async function importarCronogramas() {
    const fileInput = document.getElementById('fileCronogramas');
    const resultDiv = document.getElementById('resultCronogramas');
    
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Selecione um arquivo</div>';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    resultDiv.innerHTML = '<div class="loading"></div> Importando...';
    
    try {
        const response = await fetch(`${API_URL}/importacao/cronogramas`, {
            method: 'POST',
            headers: getHeaders(),
            body: formData
        });
        
        const result = await response.json();
        
        if (result.sucesso) {
            let html = `<div class="alert alert-success">
                <strong>Sucesso!</strong> ${result.registros_importados} registro(s) importado(s).
            </div>`;
            
            if (result.erros.length > 0) {
                html += `<div class="alert alert-warning">
                    <strong>Avisos:</strong><br>${result.erros.slice(0, 5).join('<br>')}
                </div>`;
            }
            
            resultDiv.innerHTML = html;
            fileInput.value = '';
        } else {
            resultDiv.innerHTML = '<div class="alert alert-danger">Erro na importação</div>';
        }
    } catch (error) {
        resultDiv.innerHTML = '<div class="alert alert-danger">Erro ao processar arquivo</div>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!getToken()) {
        window.location.href = '/';
        return;
    }
});
