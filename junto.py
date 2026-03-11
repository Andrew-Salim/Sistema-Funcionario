import customtkinter as ctk
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ──────────────────────────────────────────────
# BANCO DE DADOS (SQLAlchemy)
# ──────────────────────────────────────────────

# Cria/conecta ao arquivo do banco
db = create_engine("sqlite:///meubanco.db")
Session = sessionmaker(bind=db)
session = Session()
Base = declarative_base()

# Tabela de usuários (do seu colega)
class Usuario(Base):
    __tablename__ = "usuarios"
    id    = Column("id",    Integer, primary_key=True, autoincrement=True)
    nome  = Column("nome",  String)
    email = Column("email", String)
    senha = Column("senha", String)
    ativo = Column("ativo", Boolean)

    def __init__(self, nome, email, senha, ativo=True):
        self.nome  = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo

# Tabela de livros (do seu colega)
class Livro(Base):
    __tablename__ = "livros"
    id           = Column("id",           Integer, primary_key=True, autoincrement=True)
    titulo       = Column("titulo",       String)
    qtde_paginas = Column("qtde_paginas", Integer)
    dono         = Column("dono",         ForeignKey("usuarios.id"))

    def __init__(self, titulo, qtde_paginas, dono):
        self.titulo       = titulo
        self.qtde_paginas = qtde_paginas
        self.dono         = dono

# Tabela de funcionários (sua parte)
class Funcionario(Base):
    __tablename__ = "funcionarios"
    id              = Column("id",              Integer, primary_key=True, autoincrement=True)
    nome            = Column("nome",            String)
    salario_bruto   = Column("salario_bruto",   Float)
    desconto_inss   = Column("desconto_inss",   Float)
    desconto_irpf   = Column("desconto_irpf",   Float)
    salario_liquido = Column("salario_liquido", Float)

    def __init__(self, nome, salario_bruto, desconto_inss, desconto_irpf, salario_liquido):
        self.nome            = nome
        self.salario_bruto   = salario_bruto
        self.desconto_inss   = desconto_inss
        self.desconto_irpf   = desconto_irpf
        self.salario_liquido = salario_liquido

# Cria as tabelas no banco se ainda nao existirem
Base.metadata.create_all(bind=db)

# ──────────────────────────────────────────────
# FUNÇÕES DO BANCO
# ──────────────────────────────────────────────

def salvar_funcionario(nome, salario_bruto, inss, irpf, liquido):
    try:
        funcionario = Funcionario(
            nome            = nome,
            salario_bruto   = salario_bruto,
            desconto_inss   = inss,
            desconto_irpf   = irpf,
            salario_liquido = liquido
        )
        session.add(funcionario)   # adiciona na fila
        session.commit()           # salva no banco
        return True
    except Exception as e:
        session.rollback()         # desfaz se der erro
        print(f"Erro ao salvar: {e}")
        return False

def listar_funcionarios():
    # Busca todos os funcionários, do mais recente pro mais antigo
    return session.query(Funcionario).order_by(Funcionario.id.desc()).all()

# ──────────────────────────────────────────────
# CALCULOS DE SALARIO
# ──────────────────────────────────────────────

def calcular_inss(salario):
    # Aliquota fixa de 11%
    return salario * 0.11

def calcular_irpf(base):
    # base = salario ja descontado o INSS
    # Tabela progressiva do governo 2024
    if base <= 2259.20:
        return 0
    elif base <= 2826.65:
        return (base * 0.075) - 169.44
    elif base <= 3751.05:
        return (base * 0.15) - 381.44
    elif base <= 4664.68:
        return (base * 0.225) - 662.77
    else:
        return (base * 0.275) - 896.00

# ──────────────────────────────────────────────
# TELA DE LISTAGEM
# ──────────────────────────────────────────────

def abrir_listagem():
    janela = ctk.CTkToplevel()
    janela.title("Funcionarios Cadastrados")
    janela.geometry("720x400")
    janela.resizable(False, False)
    janela.grab_set()

    ctk.CTkLabel(janela, text="Funcionarios Cadastrados",
                 font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))

    frame = ctk.CTkScrollableFrame(janela, width=680, height=280)
    frame.pack(padx=20, pady=(0, 10))

    registros = listar_funcionarios()

    if not registros:
        ctk.CTkLabel(frame, text="Nenhum funcionario cadastrado ainda.").pack(pady=20)
    else:
        # Cabecalho da tabela
        cabecalho = ctk.CTkFrame(frame, fg_color="transparent")
        cabecalho.pack(fill="x", padx=4, pady=(0, 6))

        colunas = [("ID", 40), ("Nome", 160), ("Bruto", 120), ("INSS", 110), ("IRPF", 110), ("Liquido", 120)]
        for titulo, largura in colunas:
            ctk.CTkLabel(cabecalho, text=titulo, width=largura,
                         font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=4)

        # Uma linha por funcionario
        for f in registros:
            linha = ctk.CTkFrame(frame, fg_color=("gray85", "gray20"), corner_radius=6)
            linha.pack(fill="x", padx=4, pady=2)

            valores = [
                (str(f.id),                     40),
                (f.nome,                        160),
                (f"R$ {f.salario_bruto:.2f}",   120),
                (f"R$ {f.desconto_inss:.2f}",   110),
                (f"R$ {f.desconto_irpf:.2f}",   110),
                (f"R$ {f.salario_liquido:.2f}", 120),
            ]
            for texto, largura in valores:
                ctk.CTkLabel(linha, text=texto, width=largura, anchor="w").pack(side="left", padx=6, pady=4)

    ctk.CTkButton(janela, text="Fechar", width=120, command=janela.destroy).pack(pady=6)

# ──────────────────────────────────────────────
# TELA DE CADASTRO
# ──────────────────────────────────────────────

def abrir_cadastro():
    tela = ctk.CTk()
    tela.title("Cadastro de Funcionario")
    tela.geometry("420x580")
    tela.resizable(False, False)

    ctk.CTkLabel(tela, text="Cadastro de Funcionario",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(30, 20))

    # Campo nome
    ctk.CTkLabel(tela, text="Nome do Funcionario").pack(anchor="w", padx=40)
    campo_nome = ctk.CTkEntry(tela, placeholder_text="Digite o nome completo", width=340)
    campo_nome.pack(pady=(4, 14), padx=40)

    # Campo salario
    ctk.CTkLabel(tela, text="Salario Bruto (R$)").pack(anchor="w", padx=40)
    campo_salario = ctk.CTkEntry(tela, placeholder_text="Ex: 3500.00", width=340)
    campo_salario.pack(pady=(4, 14), padx=40)

    # Caixinha de preview
    frame_preview = ctk.CTkFrame(tela, width=340, corner_radius=10)
    frame_preview.pack(padx=40, pady=(0, 10))

    ctk.CTkLabel(frame_preview, text="Resumo do Calculo",
                 font=ctk.CTkFont(weight="bold")).pack(pady=(10, 4))

    # Variaveis que atualizam o texto na tela automaticamente
    var_bruto   = ctk.StringVar(value="R$ -")
    var_inss    = ctk.StringVar(value="R$ -")
    var_irpf    = ctk.StringVar(value="R$ -")
    var_liquido = ctk.StringVar(value="R$ -")

    # Funcao que monta uma linha "Label: Valor" no preview
    def criar_linha(texto_label, variavel):
        linha = ctk.CTkFrame(frame_preview, fg_color="transparent")
        linha.pack(fill="x", padx=14, pady=2)
        ctk.CTkLabel(linha, text=texto_label, anchor="w", width=180).pack(side="left")
        ctk.CTkLabel(linha, textvariable=variavel, anchor="e", width=120).pack(side="right")

    criar_linha("Salario Bruto:",   var_bruto)
    criar_linha("Desconto INSS:",   var_inss)
    criar_linha("Desconto IRPF:",   var_irpf)
    ctk.CTkFrame(frame_preview, height=1, fg_color="gray40").pack(fill="x", padx=14, pady=4)
    criar_linha("Salario Liquido:", var_liquido)
    ctk.CTkLabel(frame_preview, text="").pack(pady=4)

    # Label de status (mensagem de sucesso ou erro)
    label_status = ctk.CTkLabel(tela, text="")
    label_status.pack(pady=(0, 6))

    # Roda toda vez que o usuario digita — atualiza o preview
    def atualizar_preview(*args):
        texto   = campo_salario.get().strip().replace(",", ".")
        nome_ok = campo_nome.get().strip() != ""
        try:
            salario = float(texto)
            if salario <= 0:
                raise ValueError

            inss    = calcular_inss(salario)
            base    = salario - inss
            irpf    = calcular_irpf(base)
            liquido = salario - inss - irpf

            var_bruto.set(f"R$ {salario:.2f}")
            var_inss.set(f"R$ {inss:.2f}")
            var_irpf.set(f"R$ {irpf:.2f}")
            var_liquido.set(f"R$ {liquido:.2f}")

            btn_salvar.configure(state="normal" if nome_ok else "disabled")

        except ValueError:
            var_bruto.set("R$ -")
            var_inss.set("R$ -")
            var_irpf.set("R$ -")
            var_liquido.set("R$ -")
            btn_salvar.configure(state="disabled")

    campo_nome.bind("<KeyRelease>", atualizar_preview)
    campo_salario.bind("<KeyRelease>", atualizar_preview)

    # Roda quando o usuario clica em Salvar
    def ao_clicar_salvar():
        nome  = campo_nome.get().strip()
        texto = campo_salario.get().strip().replace(",", ".")

        try:
            salario = float(texto)
            if salario <= 0:
                raise ValueError
        except ValueError:
            label_status.configure(text="Salario invalido! Use numeros (ex: 3500.00)", text_color="orange")
            return

        inss    = calcular_inss(salario)
        base    = salario - inss
        irpf    = calcular_irpf(base)
        liquido = salario - inss - irpf

        if salvar_funcionario(nome, salario, inss, irpf, liquido):
            label_status.configure(text=f"{nome} salvo com sucesso!", text_color="green")
            # Limpa os campos depois de salvar
            campo_nome.delete(0, "end")
            campo_salario.delete(0, "end")
            var_bruto.set("R$ -")
            var_inss.set("R$ -")
            var_irpf.set("R$ -")
            var_liquido.set("R$ -")
            btn_salvar.configure(state="disabled")
        else:
            label_status.configure(text="Erro ao salvar. Tente novamente.", text_color="red")

    btn_salvar = ctk.CTkButton(tela, text="Salvar Funcionario",
                                width=340, state="disabled", command=ao_clicar_salvar)
    btn_salvar.pack(padx=40)

    ctk.CTkButton(tela, text="Ver Funcionarios Cadastrados",
                  width=340, fg_color="transparent",
                  border_width=1, text_color=("gray10", "gray90"),
                  command=abrir_listagem).pack(padx=40, pady=(12, 0))

    tela.mainloop()

# ──────────────────────────────────────────────
# TELA DE LOGIN
# ──────────────────────────────────────────────

def verificar_login():
    usuario = campo_usuario.get()
    senha   = campo_senha.get()

    if usuario == "as" and senha == "2024":
        resultado_login.configure(text="Login bem-sucedido!", text_color="green")
        app.after(600, lambda: (app.destroy(), abrir_cadastro()))
    else:
        resultado_login.configure(text="Usuario ou senha incorretos!", text_color="red")


# Monta a tela de login
app = ctk.CTk()
app.title("Login - Sistema RH")
app.geometry("400x400")
app.resizable(False, False)

ctk.CTkLabel(app, text="Sistema de RH",
             font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 20))

ctk.CTkLabel(app, text="Usuario").pack(anchor="w", padx=60)
campo_usuario = ctk.CTkEntry(app, placeholder_text="Digite seu usuario", width=280)
campo_usuario.pack(pady=(4, 14), padx=60)

ctk.CTkLabel(app, text="Senha").pack(anchor="w", padx=60)
campo_senha = ctk.CTkEntry(app, placeholder_text="Digite sua senha", show="*", width=280)
campo_senha.pack(pady=(4, 24), padx=60)

app.bind("<Return>", lambda e: verificar_login())

ctk.CTkButton(app, text="Entrar", width=280, command=verificar_login).pack(padx=60)

resultado_login = ctk.CTkLabel(app, text="")
resultado_login.pack(pady=14)

app.mainloop()