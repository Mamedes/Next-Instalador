import os
import shutil
import time
import pyodbc
from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy

from datavalidade import datecrypto

app = Flask(__name__)
db = SQLAlchemy(app)
app.secret_key = 'my_secret_key'
server = 'localhost\sqlexpress'  # for a named instance
database = 'bdnext'
username = 'sa'
password = '780sp'
cnxn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password,
    autocommit=True)
cursor = cnxn.cursor()
pyodbc.pooling = False


# Dashboard
@app.route('/')
def dashboard():
    try:
        # # Create cursor
        conn = cnxn
        cursor = conn.cursor()
        result = cursor.execute("SELECT IDUndSrv,NMUndSRV,NumeroLicenca,Endereco FROM tbUnidadeServico")
        unidades = cursor.fetchall()
        # # Close connection
        # # conn.close()
        if result:
            return render_template('dashboard.html', unidades=unidades)
        else:
            msg = 'Não há grupos cadastrados'
            return render_template('dashboard.html', msg=msg)
    except Exception as e:
        flash(str(e))


# Dashboard Grupo de Serviço
@app.route('/dashboard/grupo')
def dashboard_grupo():
    try:
        # Create cursor
        conn = cnxn
        cursor = conn.cursor()
        result = cursor.execute("SELECT IDGrupo,NMGrupo,NMApresentacao, TextoVocalizar FROM tbGesGrupoServico ")
        grupos = cursor.fetchall()
        # Close connection
        # conn.close()
        if result:
            return render_template('grupo_dashboard.html', grupos=grupos)
        else:
            msg = 'Não há grupos cadastrados'
            return render_template('grupo_dashboard.html', msg=msg)
    except  Exception as e:
        flash(str(e))


# Dashboard Grupo de Serviço
@app.route('/dashboard/setor')
def dashboard_setor():
    try:
        # Create cursor
        conn = cnxn
        cursor = conn.cursor()
        result = cursor.execute("SELECT IDSetor, NMSetor  FROM dbo.tbGesSetor")
        setores = cursor.fetchall()
        # Close connection
        # conn.close()
        if result:
            return render_template('setor_dashboard.html', setores=setores)
        else:
            msg = 'Não há setores cadastrados.'
            return render_template('setor_dashboard.html', msg=msg)
    except Exception as e:
        flash(str(e))


@app.route('/gerar_bd')
def gerar_base_dados():

    try:
        data_arquivo = str(time.strftime("%Y-%m-%d-%H-%M-%S"))

        # path = r"D:/test/DBZERO.BAK"
        # if os.path.isfile(path):
        #     os.remove(path)
        # pathTest = r"D:/test"
        # if(pathTest):
        #     shutil.rmtree(pathTest)
        # if(pathTest):
        #     os.makedirs(pathTest)

        cursor = cnxn.cursor()
        cursor.execute(
            r"BACKUP DATABASE [bdnext] TO  DISK = N'D:/test/"+data_arquivo+"_DBZERO.BAK' WITH NOFORMAT, NOINIT,  NAME = N'next.bak', SKIP, NOREWIND, NOUNLOAD,  STATS = 10")
        while (cursor.nextset()):
            pass
        path = "D:/test/"+data_arquivo+"_DBZERO.BAK"
        return send_file(path, as_attachment=True, cache_timeout=0)
        # return redirect(url_for('dashboard'))
    except Exception as e:
        flash('Error ao gerar base de dados'+str(e), 'danger')
        return redirect(url_for('dashboard'))
    except OSError as e:
        flash('Error ao gerar arquivo base de dados'+str(e), 'danger')
        return redirect(url_for('dashboard'))


# Dashboard
@app.route('/delete_bd')
def apagar_base_dados():
    try:
        pathTest = r"D:/test"
        if (pathTest):
            shutil.rmtree(pathTest)

        # Create cursor
        cursor = cnxn.cursor()
        IDUndSrv = 1
        NMUndSRV = ''
        Endereco = ''
        Bairro = ''
        tagAtivo = 1
        CEP = ''
        NMImpressao = ''
        NumeroLicenca = ''
        cursor.execute("""UPDATE tbUnidadeServico SET NMUndSRV = ?,Endereco = ?,Bairro = ?,CEP = ?,NMImpressao = ?, 
                       tagAtivo = ?,NumeroLicenca = ? WHERE IDUndSrv =? """,
                       (NMUndSRV, Endereco, Bairro, CEP, NMImpressao, tagAtivo, NumeroLicenca, IDUndSrv))

        cursor.execute("DELETE FROM tbUnidadeServico WHERE IDUndSrv != 1")
        cursor.execute("DELETE FROM tbGesSetorGrupoServico ")
        cursor.execute("DELETE FROM tbGesGrupoServico")
        cursor.execute("DELETE FROM tbGesOperadorOciosoAux WHERE IDOperador !=0")
        cursor.execute("DELETE FROM dbo.tbGesSenhaAux WHERE IDUndSrv != 1")
        cursor.execute("DELETE FROM tbUnidadeServicoModulo")
        cursor.execute("DELETE FROM dbo.tbOperadorAcesso")
        cursor.execute("DELETE FROM dbo.tbGesEstacao ")
        cursor.execute("DELETE FROM tbGesSetorOperador")
        cursor.execute("DELETE FROM tbGesSetorFaixaSenha")
        cursor.execute("DELETE FROM tbGesSetor")

        cursor.execute("SELECT MAX(IDSetor) FROM tbGesSetorFaixaSenha")
        result = cursor.fetchone()
        cursor.execute("SELECT MAX(IDModulo) FROM tbUnidadeServicoModulo")
        result1 = cursor.fetchone()
        cursor.commit()
        if (pathTest):
            os.makedirs(pathTest)

        if (result[0] == None and result1[0] == None):
            flash('Base de dados zerada', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Error ao zerar base de dados', 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash('Error ao zerar base de dados'+str(e), 'danger')
        return redirect(url_for('dashboard'))


@app.route('/unidade/add', methods=['GET', 'POST'])
def add_unidade():
    conn = cnxn
    cursor = conn.cursor()
    cursor.execute("SELECT IDUf, NMUf FROM tbUf")
    estados = cursor.fetchall()

    if request.method == 'POST':
        try:
            cursor.execute("DELETE FROM tbUnidadeServicoModulo")
            IDModulo = 1
            DataVal = datecrypto()
            cursor.execute("SELECT MAX(IDUndSrv) FROM tbUnidadeServico")
            IDUndSrv = cursor.fetchone()
            IDUndSrv = 1
            NMUndSRV = request.form.get('NMUndSRV')
            Endereco = request.form.get('endereco')
            Bairro = request.form.get('bairro')
            IDCidade = request.form['cidade']
            tagAtivo = 1
            CEP = request.form.get('cep')
            NMImpressao = request.form.get('NMImpressao')
            NumeroLicenca = request.form.get('NumeroLicenca')
            if (NMUndSRV == '' or Endereco == '' or Bairro == '' or NMImpressao == '' or NumeroLicenca == ''
                    or IDCidade == '--- Selecione Cidade ---' or CEP == ''):
                flash('Error ao criar unidade por favor, preencha os campos ', 'danger')
            else:
                conn = cnxn
                cursor = conn.cursor()
                # cursor.execute(
                #     '''INSERT INTO tbUnidadeServico (IDUndSrv, NMUndSRV, Endereco, Bairro, IDCidade, CEP, NMImpressao,
                #     tagAtivo, NumeroLicenca)
                #          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                #     (IDUndSrv, NMUndSRV, Endereco, Bairro, IDCidade, CEP, NMImpressao, tagAtivo, NumeroLicenca))

                cursor.execute("""
                                   UPDATE tbUnidadeServico SET NMUndSRV = ?,Endereco = ?,Bairro = ?,IDCidade = ?,CEP = ?,
                                   NMImpressao = ?, tagAtivo = ?,NumeroLicenca = ? WHERE IDUndSrv =? """,
                               (NMUndSRV, Endereco, Bairro, IDCidade, CEP, NMImpressao, tagAtivo, NumeroLicenca,
                                IDUndSrv))

                #  validade para MAIS DEZ ANOS a partir da data que está sendo gerado o novo BD
                for i in range(3):
                    cursor.execute(
                        '''INSERT INTO tbUnidadeServicoModulo (IDUndSrv, IDModulo, DataVal) VALUES (?, ?, ?)''',
                        (IDUndSrv, (i), DataVal))
                conn.commit()
                flash('Unidade criada', 'success')
                return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Error ao criar unidade', 'danger')
    return render_template('cadastro_unidade.html', estados=estados)


@app.route('/unidade/cidade/<get_cidade>')
def cidadebyestado(get_cidade):
    conn = cnxn
    cursor = conn.cursor()
    cursor.execute("SELECT IDCidade, NMCidade  FROM tbcidade WHERE IDUf = ?", [get_cidade])
    state_data = cursor.fetchall()
    cidadeArray = []
    for IDCidade, NMCidade in state_data:
        cidadeObj = {}
        cidadeObj['IDCidade'] = IDCidade
        cidadeObj['NMCidade'] = NMCidade
        cidadeArray.append(cidadeObj)

    return jsonify({'cidadeestado': cidadeArray})


# Add Grupo Services
@app.route('/grupo/add', methods=['GET', 'POST'])
def add_grupo_service():
    if request.method == 'POST':
        try:
            conn = cnxn
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(IDGrupo) FROM tbGesGrupoServico")
            result = cursor.fetchone()
            if (result[0] == None):
                IDGrupo = 1
            else:
                IDGrupo = int(result[0]) + 1

            NMGrupo = request.form.get('NMGrupo')
            NMApresentacao = request.form.get('NMApresentacao')
            TextoVocalizar = request.form.get('TextoVocalizar')
            tagSigla = request.form.get('utiliza_sigla')
            if (tagSigla == None):
                tagSigla = 0
            NMSigla = request.form.get('NMSigla')

            tagExibirNaEmissaoDaSenha = request.form.get('exbibir_grupo_service_senha')
            if (tagExibirNaEmissaoDaSenha == None):
                tagExibirNaEmissaoDaSenha = 0
            IDSitGrupo = 1
            tagTempoNMATD = 0
            tagVocalizaSigla = 0
            Color = 0

            if (NMGrupo == '' or NMApresentacao == '' or TextoVocalizar == ''):
                flash('Error ao criar grupo de serviço por favor, preencha os campos ', 'danger')
            elif ((tagSigla == '1' and NMSigla == '') or (tagSigla == 0 and NMSigla != '')):
                flash('Erro, no preenchimento dos campo utiliza sigla e sigla', 'danger')
            else:
                cursor.execute(
                    '''INSERT INTO tbGesGrupoServico 
                     (
                     IDGrupo,
                     NMGrupo,
                     NMApresentacao, 
                     TextoVocalizar, 
                     tagSigla, 
                     NMSigla,
                     tagExibirNaEmissaoDaSenha,
                     IDSitGrupo,
                    tagTempoNMATD, 
                    tagVocalizaSigla,
                    Color)
                    VALUES (?,?, ?,?,?,?,?,?,?,?,?)''',
                    (
                        IDGrupo,
                        NMGrupo,
                        NMApresentacao,
                        TextoVocalizar,
                        tagSigla,
                        NMSigla,
                        tagExibirNaEmissaoDaSenha,
                        IDSitGrupo,
                        tagTempoNMATD,
                        tagVocalizaSigla,
                        Color
                    )
                )
                cursor.commit()
                flash('Grupo de serviço  criado', 'success')
                return redirect(url_for('dashboard_grupo'))
        except Exception as e:
            flash('Error ao criar grupo de serviço' + str(e), 'danger')
    return render_template('cadastro_grupo.html')



@app.route('/dashboard/setor/add', methods=['GET', 'POST'])
def add_setor():
    nome_unidade = ''
    frase_1 = "Seja Bem vindo "
    cursor = cnxn.cursor()
    cursor.execute("SELECT IDUndSrv, NMUndSRV FROM tbunidadeservico")
    unidades = cursor.fetchall()

    if request.method == 'POST':
        try:
            IDUndSrv = int(request.form.get('unidade'))
            session['IDUndSrv'] = IDUndSrv
            session['NMSetor'] = request.form.get('name_setor')

            if session['NMSetor'] == '':
                flash('Error ao criar setor preencha todos os campos', 'danger')

            else:
                IDUndSrv = int(request.form.get('unidade'))
                session['IDUndSrv'] = IDUndSrv
                session['NMSetor'] = request.form.get('name_setor')
                # Rotina pra buscar o nome da unidade pra exibir na variavel frase_1
                for u in unidades:
                    if u[0] == IDUndSrv:
                        nome_unidade = u[1]
                session['FraseMonitor1'] = frase_1 + nome_unidade
                return redirect(url_for('setor_grupo'))
        except ValueError as e:
            flash('Selecione unidade', 'warning')
        except Exception as e:
            flash('Error ao criar setor', 'danger')
    return render_template('cadastro_setor.html', frase_1=frase_1, unidades=unidades)


tbGesSetorGrupoServico = []


@app.route('/setor/grupo/add', methods=['GET', 'POST'])
def setor_grupo():
    cursor = cnxn.cursor()
    cursor.execute("SELECT IDGrupo, NMGrupo FROM tbGesGrupoServico")
    ges_grupos = cursor.fetchall()

    if request.method == 'POST':
        try:
            ges_grupos1 = request.form.get('ges_grupo')
            hora_inicio = request.form.get('hora_inicio')
            hora_final = request.form.get('hora_final')
            input_tipo_senha = request.form.get('input_tipo_senha')
            exibir_senha = request.form.get('input_exibir_senha')

            if (ges_grupos1 == '--- Selecione Grupo de Serviço ---' or hora_inicio == '' or
                    hora_final == '' or input_tipo_senha == 'Selecione Tipo Senha...' or exibir_senha == 'Selecione Exibir Senha Monitor...'):
                flash('Informe todos os campos', 'warning')
            else:
                tbGesSetorGrupoServico.append(request.form.get('ges_grupo'))
                tbGesSetorGrupoServico.append(request.form.get('hora_inicio'))
                tbGesSetorGrupoServico.append(request.form.get('hora_final'))
                tbGesSetorGrupoServico.append(request.form.get('input_tipo_senha'))
                tbGesSetorGrupoServico.append(request.form.get('input_exibir_senha'))

                session['tbGesSetorGrupoServico'] = tbGesSetorGrupoServico
                flash('Grupo Cadastrado com sucesso', 'success')
                return redirect(url_for('setor_grupo'))

        except Exception as e:
            flash('Error ao criar grupo' + str(e), 'danger')
    return render_template('cadastro_setor_grupo.html', ges_grupos=ges_grupos)


@app.route('/setor/faixa', methods=['GET', 'POST'])
def setor_faixa():
    tamanhotbGesSetorGrupoServico = len(tbGesSetorGrupoServico)
    if (tamanhotbGesSetorGrupoServico == 0):
        error = 'Não há grupo de serviço cadastrados.'
        return render_template('cadastro_setor_grupo.html', error=error)

    if request.method == 'POST':
        try:
            pref80_faixa_inicio = int(request.form.get('pref80_faixa_inicio'))
            pref80_faixa_final = int(request.form.get('pref80_faixa_final'))
            pref_faixa_inicio = int(request.form.get('pref_faixa_inicio'))
            pref_faixa_inicio = int(request.form.get('pref_faixa_inicio'))
            pref_faixa_final = int(request.form.get('pref_faixa_final'))
            normal_faixa_inicio = int(request.form.get('normal_faixa_inicio'))
            normal_faixa_final = int(request.form.get('normal_faixa_final'))

            tbGesSetorFaixaSenha = \
                [
                    (1, request.form.get('pref80_faixa_inicio'), request.form.get('pref80_faixa_final')),
                    (2, request.form.get('pref_faixa_inicio'), request.form.get('pref_faixa_final')),
                    (3, request.form.get('normal_faixa_inicio'), request.form.get('normal_faixa_final')),
                ]

            session['tbGesSetorFaixaSenha'] = tbGesSetorFaixaSenha
            return redirect(url_for('setor_parametro'))
        except ValueError:
            flash("Erro informe todos os campos, apenas numeros!", 'danger')
        except Exception as e:
            flash('Error ao criar setor faixa de senha ' + str(e), 'danger')
    return render_template('cadastro_setor_faixa_senha.html')


@app.route('/setor/parametro', methods=['GET', 'POST'])
def setor_parametro():

    if request.method == 'POST':
        try:
            listatbGesSetorFaixaSenha = session['tbGesSetorFaixaSenha']
            conn = cnxn
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(IDSetor) FROM tbGesSetor")
            result = cursor.fetchone()

            if (result[0] == None):
                IDSetor = 1
            else:
                IDSetor = int(result[0]) + 1

            IDUndSrv = session['IDUndSrv']
            NMSetor = session['NMSetor']
            IDSitSetor = 1
            FraseMonitor1 = session["FraseMonitor1"]
            tagEmissorMonitor = request.form.get('emissormonitor')
            if (tagEmissorMonitor == None):
                tagEmissorMonitor = 0

            tagAtend24Horas = request.form.get('atendimento24horas')
            if (tagAtend24Horas == None):
                tagAtend24Horas = 0

            tagImprimirTempoMedioEsp = 0
            tagUtilizarObervacao = request.form.get('utilizaobservacao')
            if (tagUtilizarObervacao == None):
                tagUtilizarObervacao = 0

            tagImprimirObservacao = 0
            tagInformarObservacaoEmissao = 0
            tagImpInfSenha = 0
            IDModeloEmissorSenha = 1  # Modelo Emissor de Senha
            AlinhamentoTexto = 'j'  # Alinhamento de Texto
            IDModeloMonitor = 1  # Modelo Monitor Padrão
            IDTipoSenha = session["FraseMonitor1"]
            FaixaInicial = session["FraseMonitor1"]
            FaixaFinal = session["FraseMonitor1"]

            cursor.execute(
                '''INSERT INTO tbGesSetor (IDSetor, IDUndSrv, NMSetor, IDSitSetor, FraseMonitor1, tagEmissorMonitor, tagAtend24Horas, tagImprimirTempoMedioEsp,
                tagUtilizarObervacao, tagImprimirObservacao,tagInformarObservacaoEmissao,tagImpInfSenha,IDModeloEmissorSenha,AlinhamentoTexto,IDModeloMonitor)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (IDSetor, IDUndSrv, NMSetor, IDSitSetor, FraseMonitor1, tagEmissorMonitor, tagAtend24Horas,
                 tagImprimirTempoMedioEsp,
                 tagUtilizarObervacao, tagImprimirObservacao, tagInformarObservacaoEmissao, tagImpInfSenha,
                 IDModeloEmissorSenha, AlinhamentoTexto, IDModeloMonitor))

            for t in listatbGesSetorFaixaSenha:
                cursor.execute('''INSERT INTO tbGesSetorFaixaSenha (IDSetor, IDTipoSenha, FaixaInicial, FaixaFinal)
                                                     VALUES (?, ?, ?, ?)''', (IDSetor, t[0], t[1], t[2]))

            i = -1
            x = len(session['tbGesSetorGrupoServico'])

            tb_GesSetorGrupoServico = session['tbGesSetorGrupoServico']
            x = (len(tb_GesSetorGrupoServico))
            tagExibirEmissorSenha = 1
            for t in range(int(x / 5)):
                cursor.execute(
                    '''INSERT INTO tbGesSetorGrupoServico (IDSetor,IDGrupo, HoraIni, HoraFim, Tipo, TipoExibe, tagExibirEmissorSenha) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (
                        IDSetor, tb_GesSetorGrupoServico[i + 1], tb_GesSetorGrupoServico[i + 2],
                        tb_GesSetorGrupoServico[i + 3],
                        tb_GesSetorGrupoServico[i + 4], tb_GesSetorGrupoServico[i + 5], tagExibirEmissorSenha))
                i += 5
            cursor.commit()
            tb_GesSetorGrupoServico = []
            tbGesSetorGrupoServico.clear()
            session['tbGesSetorGrupoServico']
        except Exception as e:
            flash('Error ao criar parametro'+ str(e), 'danger')
        return redirect(url_for('dashboard_setor'))
    return render_template('cadastro_setor_parametro.html')


if __name__ == '__main__':
        #app.run(host='192.168.201.117', port=3333)
         app.run(debug=True)
