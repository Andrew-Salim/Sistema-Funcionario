import customtkinter as ctk
from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ──────────────────────────────────────────────
# BANCO DE DADOS (SQLAlchemy)
# ──────────────────────────────────────────────

db = create_engine("sqlite:///meubanco.db")
Session = sessionmaker(bind=db)
session = Session()
Base = declarative_base()

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

class Funcionario(Base):
    __tablename__ = "funcionarios"
    id      = Column("id",      Integer, primary_key=True, autoincrement=True)
    nome    = Column("nome",    String)
    salario = Column("salario", Integer)

    def __init__(self, nome, salario):
        self.nome    = nome
        self.salario = salario

# Cria todas as tabelas no banco
Base.metadata.create_all(bind=db)

# ──────────────────────────────────────────────
# FUNÇÕES DO BANCO
# ──────────────────────────────────────────────

def salvar_funcionario(nome: str, salario: float) -> bool:
    try:
        funcionario = Funcionario(nome=nome.strip(), salario=salario)
        session.add(funcionario)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Erro ao salvar funcionário: {e}")
        return False

def listar_funcionarios() -> list:
    return session.query(Funcionario).order_by(Funcionario.id.desc()).all()

# ──────────────────────────────────────────────
# TELA DE LISTAGEM
# ──────────────────────────────────────────────

def abrir_listagem():
    janela = ctk.CTkToplevel()
    janela.title("Funcionários Cadastrados")
    janela.geometry("480x400")
    janela.resizable(False, False)
    janela.grab_set()

    ctk.CTkLabel(
        janela, text="Funcionários Cadastrados",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(pady=(20, 10))

    frame = ctk.CTkScrollableFrame(janela, width=440, height=280)
    frame.pack(padx=20, pady=(0, 10))

    registros = listar_funcionarios()

    if not registros:
        ctk.CTkLabel(frame, text="Nenhum funcionário cadastrado ainda.").pack(pady=20)
    else:
        # Cabeçalho
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=4, pady=(0, 6))
        for col, w in [("ID", 50), ("Nome", 250), ("Salário", 120)]:
            ctk.CTkLabel(
                header, text=col, width=w,
                font=ctk.CTkFont(weight="bold"), anchor="w"
            ).pack(side="left", padx=4)

        # Linhas
        for f in registros:
            row = ctk.CTkFrame(frame, fg_color=("gray85", "gray20"), corner_radius=6)
            row.pack(fill="x", padx=4, pady=2)
            for val, w in [(str(f.id), 50), (f.nome, 250), (f"R$ {f.salario:,.2f}", 120)]:
                ctk.CTkLabel(row, text=val, width=w, anchor="w").pack(side="left", padx=6, pady=4)

    ctk.CTkButton(janela, text="Fechar", width=120, command=janela.destroy).pack(pady=6)

# ──────────────────────────────────────────────
# TELA DE CADASTRO
# ──────────────────────────────────────────────

def abrir_cadastro_standalone():
    cadastro = ctk.CTk()
    _montar_cadastro(cadastro)
    cadastro.mainloop()

def _montar_cadastro(janela):
    janela.title("Cadastro de Funcionário")
    janela.geometry("400x460")
    janela.resizable(False, False)

    ctk.CTkLabel(
        janela, text="Cadastro de Funcionário",
        font=ctk.CTkFont(size=20, weight="bold"),
    ).pack(pady=(30, 20))

    ctk.CTkLabel(janela, text="Nome do Funcionário").pack(anchor="w", padx=40)
    entry_nome = ctk.CTkEntry(janela, placeholder_text="Digite o nome completo", width=340)
    entry_nome.pack(pady=(4, 14), padx=40)

    ctk.CTkLabel(janela, text="Salário (R$)").pack(anchor="w", padx=40)
    entry_salario = ctk.CTkEntry(janela, placeholder_text="Ex: 3500.00", width=340)
    entry_salario.pack(pady=(4, 20), padx=40)

    label_status = ctk.CTkLabel(janela, text="")
    label_status.pack(pady=(0, 10))

    def verificar_campos(*args):
        nome_ok    = entry_nome.get().strip() != ""
        salario_ok = entry_salario.get().strip() != ""
        btn_salvar.configure(state="normal" if (nome_ok and salario_ok) else "disabled")

    entry_nome.bind("<KeyRelease>", verificar_campos)
    entry_salario.bind("<KeyRelease>", verificar_campos)

    def ao_salvar():
        nome = entry_nome.get().strip()
        raw  = entry_salario.get().strip().replace(",", ".")
        try:
            salario = float(raw)
            if salario < 0:
                raise ValueError
        except ValueError:
            label_status.configure(text="⚠ Salário inválido! Use números (ex: 3500.00)", text_color="orange")
            return

        if salvar_funcionario(nome, salario):
            label_status.configure(text=f"✔ {nome} salvo com sucesso!", text_color="green")
            entry_nome.delete(0, "end")
            entry_salario.delete(0, "end")
            btn_salvar.configure(state="disabled")
        else:
            label_status.configure(text="✘ Erro ao salvar. Tente novamente.", text_color="red")

    btn_salvar = ctk.CTkButton(janela, text="Salvar", width=340, state="disabled", command=ao_salvar)
    btn_salvar.pack(padx=40)

    ctk.CTkButton(
        janela, text="Ver Funcionários Cadastrados",
        width=340, fg_color="transparent",
        border_width=1, text_color=("gray10", "gray90"),
        command=abrir_listagem
    ).pack(padx=40, pady=(12, 0))

# ──────────────────────────────────────────────
# TELA DE LOGIN
# ──────────────────────────────────────────────

def validar_login():
    usuario = campo_usuario.get()
    senha   = campo_senha.get()

    if usuario == "as" and senha == "2024":
        resultado_login.configure(text="Login bem-sucedido!", text_color="green")
        app.after(600, lambda: (app.destroy(), abrir_cadastro_standalone()))
    else:
        resultado_login.configure(text="Usuário ou senha incorretos!", text_color="red")


app = ctk.CTk()
app.title("Login")
app.geometry("400x400")
app.resizable(False, False)

ctk.CTkLabel(app, text="Sistema de Login", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 20))

ctk.CTkLabel(app, text="Usuário").pack(anchor="w", padx=60)
campo_usuario = ctk.CTkEntry(app, placeholder_text="Digite seu usuário", width=280)
campo_usuario.pack(pady=(4, 14), padx=60)

ctk.CTkLabel(app, text="Senha").pack(anchor="w", padx=60)
campo_senha = ctk.CTkEntry(app, placeholder_text="Digite sua senha", show="*", width=280)
campo_senha.pack(pady=(4, 24), padx=60)

app.bind("<Return>", lambda e: validar_login())

ctk.CTkButton(app, text="Entrar", width=280, command=validar_login).pack(padx=60)

resultado_login = ctk.CTkLabel(app, text="")
resultado_login.pack(pady=14)

app.mainloop()