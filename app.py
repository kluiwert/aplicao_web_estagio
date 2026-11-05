from flask import Flask, render_template, request, redirect, url_for, flash
from livereload import Server
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = 'chave_provisoria_para_desenvolvimento_ufam'
app.debug = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def pagina_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def processar_login():
    matricula = request.form.get('matricula')
    senha = request.form.get('senha')
    return redirect(url_for('pagina_painel'))

@app.route('/cadastro', methods=['GET', 'POST'])
def pagina_cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        flash('Solicitação de cadastro enviada com sucesso! Aguarde a liberação.', 'success')
        return redirect(url_for('pagina_login'))
    return render_template('cadastro.html')

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def pagina_esqueci_senha():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        flash('Se os dados estiverem corretos, as instruções foram enviadas para seu e-mail.', 'info')
        return redirect(url_for('pagina_login'))
    return render_template('esqueci_senha.html')

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

# LISTA TEMPORÁRIA PARA ARMAZENAR OS PEDIDOS DE "AVISE-ME"
LISTA_ESPERA_AVISOS = []

# DICIONÁRIO PARA ARMAZENAR NOTIFICAÇÕES PENDENTES PARA OS ALUNOS
NOTIFICACOES_ALUNOS = {}

@app.route('/painel', methods=['GET', 'POST'])
def pagina_painel():
    # Simulando o aluno logado atualmente no sistema como "João Silva"
    aluno_atual = "João Silva"
    
    # Verifica se existem notificações geradas pelo admin para este aluno
    if aluno_atual in NOTIFICACOES_ALUNOS and NOTIFICACOES_ALUNOS[aluno_atual]:
        for aviso in NOTIFICACOES_ALUNOS[aluno_atual]:
            flash(aviso, 'info') # Gera o pop-up de aviso na tela do aluno
        # Limpa as notificações para não duplicarem ao atualizar a página
        NOTIFICACOES_ALUNOS[aluno_atual] = []

    if request.method == 'POST':
        data_retirada_str = request.form.get('data_retirada')
        justificativa = request.form.get('justificativa')
        observacoes = request.form.get('observacoes')
        
        if justificativa == 'outro':
            justificativa = request.form.get('justificativa_outro')
        
        try:
            data_retirada_obj = datetime.strptime(data_retirada_str, '%Y-%m-%dT%H:%M')
            data_devolucao_obj = data_retirada_obj + timedelta(days=7)
            data_devolucao_formatada = data_devolucao_obj.strftime('%d/%m/%Y às %H:%M')
            flash(f'Reserva solicitada! Devolução: {data_devolucao_formatada}. Motivo registrado: {justificativa}', 'success')
        except ValueError:
            flash('Erro ao processar as datas. Tente novamente.', 'danger')
            
        return redirect(url_for('pagina_painel'))

    return render_template('painel.html', equipamentos=EQUIPAMENTOS, reservas=RESERVAS_ATIVAS)

# ROTA PARA PROCESSAR O CLIQUE DO ALUNO NO BOTÃO "AVISE-ME"
@app.route('/solicitar-aviso', methods=['POST'])
def solicitar_aviso():
    equipamento_id = request.form.get('equipamento_id')
    
    aluno_nome = "João Silva"
    aluno_email = "joao.silva@ufam.edu.br"
    aluno_telefone = "+55 92 99111-2233"
    
    equipamento_encontrado = next((e for e in EQUIPAMENTOS if str(e['id']) == str(equipamento_id)), None)
    nome_equipamento = equipamento_encontrado['nome'] if equipamento_encontrado else "Equipamento"
    patrimonio_equipamento = equipamento_encontrado['patrimonio'] if equipamento_encontrado else "EE-LAB-XXX"
    
    nova_solicitacao = {
        'aluno': aluno_nome,
        'matricula': '21900123',
        'equipamento': nome_equipamento,
        'patrimonio': patrimonio_equipamento,
        'status': 'Aguardando liberação'
    }
    LISTA_ESPERA_AVISOS.append(nova_solicitacao)
    
    print(f"\n[LOG EMAIL] Enviando confirmação para {aluno_email}: Você foi inserido na lista de espera para '{nome_equipamento}'.")
    print(f"[LOG WHATSAPP] Mensagem disparada para {aluno_telefone}: Olá {aluno_nome}, confirmamos seu pedido de aviso para o item {patrimonio_equipamento}!\n")
    
    flash(f'Inscrição confirmada! Um aviso foi enviado para seu e-mail ({aluno_email}) e WhatsApp.', 'success')
    return redirect(url_for('pagina_painel'))

@app.route('/login-admin', methods=['GET', 'POST'])
def pagina_login_admin():
    if request.method == 'POST':
        return redirect(url_for('pagina_painel_admin'))
    return render_template('login_admin.html')

@app.route('/painel-admin')
def pagina_painel_admin():
    return render_template('painel_admin.html')

# ROTA PARA EXIBIR A TELA DE GERENCIAMENTO DE ESTOQUE DO ADMIN
@app.route('/painel-admin/estoque')
def pagina_estoque_admin():
    return render_template('painel_admin_estoque.html', equipamentos=EQUIPAMENTOS)

# ROTA PARA PROCESSAR AS AÇÕES DO MODAL (APAGAR, DESABILITAR, ATUALIZAR QTD)
@app.route('/painel-admin/estoque/atualizar', methods=['POST'])
def atualizar_estoque():
    equipamento_id = int(request.form.get('id'))
    acao = request.form.get('acao') # Pode vir como: 'salvar', 'desabilitar', 'habilitar', 'apagar'
    
    global EQUIPAMENTOS

    if acao == 'apagar':
        # Remove o item da lista
        EQUIPAMENTOS = [e for e in EQUIPAMENTOS if e['id'] != equipamento_id]
        flash('Equipamento apagado do sistema com sucesso!', 'success')
        
    else:
        # Busca o equipamento na lista para atualizar
        for e in EQUIPAMENTOS:
            if e['id'] == equipamento_id:
                if acao == 'desabilitar':
                    e['status'] = 'bloqueado'
                    flash(f'O equipamento {e["nome"]} foi desabilitado/bloqueado.', 'warning')
                
                elif acao == 'habilitar':
                    e['status'] = 'disponivel'
                    flash(f'O equipamento {e["nome"]} agora está disponível.', 'success')
                
                elif acao == 'salvar':
                    nova_qtd = int(request.form.get('quantidade', e['estoque_total']))
                    e['estoque_total'] = nova_qtd
                    # Logica simples: se ajustou o total, garante que o disponível não exceda o total
                    if e['estoque_disp'] > nova_qtd:
                        e['estoque_disp'] = nova_qtd
                    flash(f'Quantidade atualizada para {nova_qtd}!', 'success')
                break

    return redirect(url_for('pagina_estoque_admin'))


@app.route('/painel-admin/cadastro-materiais', methods=['GET', 'POST'])
def pagina_cadastro_materiais():
    if request.method == 'POST':
        nome_equipamento = request.form.get('nome_equipamento')
        return redirect(url_for('pagina_cadastro_materiais'))
    return render_template('painel_admin_cadastro_materiais.html')

@app.route('/painel-admin/controle-alunos')
def pagina_controle_alunos():
    return render_template('painel_admin_alunos.html')

@app.route('/painel-admin/reservas-pendentes')
def pagina_reservas_pendentes():
    return render_template('painel_admin_reservas.html', solicitacoes_aviso=LISTA_ESPERA_AVISOS)

# ROTA PARA O ADMINISTRADOR NOTIFICAR A DISPONIBILIDADE DO EQUIPAMENTO AO ALUNO
@app.route('/painel-admin/notificar/<string:nome_aluno>/<string:nome_equipamento>', methods=['POST'])
def notificar_aluno(nome_aluno, nome_equipamento):
    mensagem = f"Boa notícia! O equipamento '{nome_equipamento}' que você solicitou na lista de espera agora está disponível para retirada."
    
    if nome_aluno not in NOTIFICACOES_ALUNOS:
        NOTIFICACOES_ALUNOS[nome_aluno] = []
    NOTIFICACOES_ALUNOS[nome_aluno].append(mensagem)
    
    flash(f"Notificação de disponibilidade enviada com sucesso para {nome_aluno}!", "success")
    return redirect(url_for('pagina_reservas_pendentes'))

@app.route('/estagiario')
def pagina_estagiario():
    return render_template('painel_estagiario.html')

@app.route('/estagiario/atendimento', methods=['POST'])
def processar_atendimento_estagiario():
    aluno = request.form.get('aluno')
    equipamento = request.form.get('equipamento')
    observacoes = request.form.get('observacoes')
    foto = request.files.get('foto')
    if foto:
        pass
    return redirect(url_for('pagina_estagiario'))

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('templates/')
    server.watch('static/')
    server.serve(port=3000)