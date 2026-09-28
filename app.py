"""
SISTEMA DE GERENCIAMENTO DE RESERVAS - LAB. DE CONTROLE E ENERGIA (FEEC/UFAM)
===========================================================================
Descrição: 
Este arquivo contém as rotas e o servidor back-end estruturado em Flask.
Inclui correções para garantir que o LiveReload não quebre os redirecionamentos,
além de rotas separadas para o fluxo de alunos e o fluxo da administração.
"""

# Importação das bibliotecas necessárias do Flask para renderizar telas, gerenciar requisições e exibir mensagens
from flask import Flask, render_template, request, redirect, url_for, flash
# Importação do servidor LiveReload para atualizar a página automaticamente durante o desenvolvimento
from livereload import Server
# IMPORTAÇÃO DE FERRAMENTAS DE DATA E HORA
from datetime import datetime, timedelta

# Inicializa a aplicação Flask
app = Flask(__name__)

# =========================================================================
# CONFIGURAÇÕES DO SERVIDOR
# =========================================================================

# Chave secreta obrigatória para ativar o recurso 'flash' (mensagens temporárias de sucesso/erro)
app.secret_key = 'chave_provisoria_para_desenvolvimento_ufam'

# ATIVAÇÃO DO MODO DEBUG: 
# Essencial para que erros sejam exibidos no terminal e para que o LiveReload processe redirecionamentos corretamente
app.debug = True
# Garante que o Flask recarregue os arquivos HTML caso eles sejam modificados
app.config['TEMPLATES_AUTO_RELOAD'] = True


# =========================================================================
# ROTAS PÚBLICAS (AUTENTICAÇÃO E CADASTRO)
# =========================================================================

@app.route('/')
def pagina_login():
    """Renderiza a tela inicial de Login para usuários comuns (Alunos)."""
    # Apenas carrega e exibe o arquivo HTML de login
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def processar_login():
    """Processa as credenciais enviadas pelo formulário de login."""
    # Captura os dados que o usuário digitou nos campos de input do formulário
    matricula = request.form.get('matricula')
    senha = request.form.get('senha')
    lembrar_me = request.form.get('lembrar_me')

    # Futuramente: Aqui haverá uma verificação na base de dados para ver se a matrícula e senha estão corretas.
    # Por enquanto, força o redirecionamento direto para a página do painel do aluno.
    return redirect(url_for('pagina_painel'))


@app.route('/cadastro', methods=['GET', 'POST'])
def pagina_cadastro():
    """GET: Exibe o formulário de cadastro. POST: Recebe dados e volta ao login."""
    # Se o usuário clicou no botão "Finalizar Cadastro", o método será POST
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        
        # Otimização: Feedback visual indicando que a ação funcionou (aparecerá na próxima tela)
        flash('Solicitação de cadastro enviada com sucesso! Aguarde a liberação.', 'success')
        
        # Após receber os dados, envia o usuário de volta para a tela inicial
        return redirect(url_for('pagina_login'))
    
    # Se o método for GET (usuário apenas clicou no link para abrir a página), mostra o HTML
    return render_template('cadastro.html')


@app.route('/esqueci-senha', methods=['GET', 'POST'])
def pagina_esqueci_senha():
    """Gerencia a tela de recuperação de senha."""
    if request.method == 'POST':
        # Captura o CPF digitado para buscar a conta
        cpf = request.form.get('cpf')
        
        # Otimização: Informa que as instruções foram geradas e enviadas
        flash('Se os dados estiverem corretos, as instruções foram enviadas para seu e-mail.', 'info')
        return redirect(url_for('pagina_login'))
        
    return render_template('esqueci_senha.html')


# =========================================================================
# BASE DE DADOS FAKE (MOCK) PARA TESTES
# =========================================================================
EQUIPAMENTOS = [
    {
        'id': 1,
        'nome': 'Osciloscópio Tektronix TBS1052B',
        'patrimonio': 'EE-LAB-014',
        'observacao': 'Pontas de prova incluídas.',
        'status': 'disponivel',
        'estoque_disp': 1,
        'estoque_total': 1,
    },
    {
        'id': 2,
        'nome': 'Multímetro Digital Fluke 87V',
        'patrimonio': 'EE-LAB-022',
        'observacao': 'Cabos inspecionados.',
        'status': 'parcial',
        'estoque_disp': 3,
        'estoque_total': 4,
    },
    {
        'id': 3,
        'nome': 'Osciloscópio Keysight EDUX1002G',
        'patrimonio': 'EE-LAB-009',
        'observacao': 'Conflito em atraso.',
        'status': 'bloqueado',
        'estoque_disp': 0,
        'estoque_total': 1,
    },
]

RESERVAS_ATIVAS = [
    {
        'patrimonio': 'EE-LAB-022',
        'nome': 'Multímetro Fluke 87V',
        'status': 'Confirmado',
        'data_devolucao': '14/09/2026',
    },
]

# =========================================================================
# ROTAS DO USUÁRIO COMUM (ÁREA LOGADA)
# =========================================================================

@app.route('/painel', methods=['GET', 'POST'])
def pagina_painel():
    """
    GERENCIA O PAINEL DO ALUNO E AS SOLICITAÇÕES DE RESERVA
    -------------------------------------------------------
    - GET: Carrega o painel.
    - POST: Captura a data de retirada, soma 7 dias automaticamente e registra.
    """
    if request.method == 'POST':
        
        # 1. CAPTURA OS DADOS DO FORMULÁRIO 
        data_retirada_str = request.form.get('data_retirada')
        justificativa = request.form.get('justificativa')
        observacoes = request.form.get('observacoes')
        
        # --- LÓGICA DO CAMPO "OUTRO" ---
        # Se o aluno escolheu "Outro", substitui o valor pela justificativa digitada no texto extra
        if justificativa == 'outro':
            justificativa = request.form.get('justificativa_outro')
        
        # 2. CÁLCULO AUTOMÁTICO DE DEVOLUÇÃO (+7 Dias)
        try:
            # Transforma a string que veio do HTML em um formato de "Relógio/Calendário" do Python
            data_retirada_obj = datetime.strptime(data_retirada_str, '%Y-%m-%dT%H:%M')
            
            # Soma exatamente 7 dias (1 semana)
            data_devolucao_obj = data_retirada_obj + timedelta(days=7)
            
            # Transforma de volta em texto legível (ex: "02/10/2026 às 14:30") para salvar ou exibir depois
            data_devolucao_formatada = data_devolucao_obj.strftime('%d/%m/%Y às %H:%M')
            
            # Exibe na mensagem verde quando o aluno vai ter que devolver, incluindo o motivo para teste!
            flash(f'Reserva solicitada! Devolução: {data_devolucao_formatada}. Motivo registrado: {justificativa}', 'success')
            
        except ValueError:
            # Caso dê algum erro invisível no formato da data
            flash('Erro ao processar as datas. Tente novamente.', 'danger')
            
        # 3. REDIRECIONAMENTO LIMPO
        return redirect(url_for('pagina_painel'))

    # 4. FLUXO NORMAL (GET): Envia as listas Python (nosso DB fake) para o ficheiro HTML desenhar a tela
    return render_template('painel.html', equipamentos=EQUIPAMENTOS, reservas=RESERVAS_ATIVAS)

# =========================================================================
# ROTAS DA ADMINISTRAÇÃO (ÁREA ADMINISTRATIVA)
# =========================================================================

@app.route('/login-admin', methods=['GET', 'POST'])
def pagina_login_admin():
    """Exibe e processa o login específico do Administrador (Técnicos/Professores)."""
    if request.method == 'POST':
        # Redireciona para o "QG" administrativo após o login bem-sucedido
        return redirect(url_for('pagina_painel_admin'))
        
    return render_template('login_admin.html')


@app.route('/painel-admin')
def pagina_painel_admin():
    """Exibe o painel de controle central do administrador (Menu com os 3 cartões)."""
    return render_template('painel_admin.html')


@app.route('/painel-admin/cadastro-materiais', methods=['GET', 'POST'])
def pagina_cadastro_materiais():
    """Gerencia o cadastro de novos materiais/equipamentos no inventário."""
    if request.method == 'POST':
        # Captura o nome do equipamento inserido no formulário para salvar no banco
        nome_equipamento = request.form.get('nome_equipamento')
        
        # Feedback de sucesso e redirecionamento para limpar o formulário
        flash('Equipamento cadastrado com sucesso no catálogo!', 'success')
        return redirect(url_for('pagina_cadastro_materiais'))
        
    return render_template('painel_admin_cadastro_materiais.html')


@app.route('/painel-admin/controle-alunos')
def pagina_controle_alunos():
    """Exibe a lista de alunos cadastrados, permitindo bloqueios e gestão de acessos."""
    # Carrega a tela com a tabela de usuários e seus status (Ativo/Bloqueado)
    return render_template('painel_admin_alunos.html')


@app.route('/painel-admin/reservas-pendentes')
def pagina_reservas_pendentes():
    """Exibe as solicitações de equipamentos aguardando aprovação ou recusa."""
    # NOTA: O nome dentro do render_template deve ser IGUAL ao nome do arquivo físico na pasta 'templates'
    return render_template('painel_admin_reservas.html')


# =========================================================================
# INICIALIZAÇÃO DO SERVIDOR COM LIVERELOAD
# =========================================================================

# O bloco abaixo só é executado se este arquivo for rodado diretamente (ex: python app.py)
if __name__ == '__main__':
    # Envolve a aplicação Flask com o servidor LiveReload
    server = Server(app.wsgi_app)
    
    # Monitora as pastas 'templates' e 'static'. 
    # Qualquer salvamento em arquivos HTML ou CSS nestas pastas fará o navegador atualizar sozinho.
    server.watch('templates/')
    server.watch('static/')
    
    # Inicializa o servidor web localmente na porta 3000 (acessível via http://127.0.0.1:3000)
    server.serve(port=3000)