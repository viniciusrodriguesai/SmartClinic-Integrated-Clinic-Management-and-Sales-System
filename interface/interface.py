"""
SmartClinic — Interface Integrada com Banco de Dados
=====================================================
Conecta a UI tkinter ao backend real (ClienteDAO + MySQL).
Certifique-se de que o arquivo secreto.env existe na raiz do projeto
com as variáveis: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

# ─── Adiciona /src ao path para importar ClienteDAO e db ───────────────
SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC_DIR))

DB_DISPONIVEL = False
_DB_ERRO_MSG  = ""
try:
    from cliente_dao import ClienteDAO, Cliente
    from db import get_conn
    with get_conn() as _conn:
        pass
    DB_DISPONIVEL = True
except Exception as _db_err:
    _DB_ERRO_MSG = str(_db_err)

# ─────────────────────────────────────────────
#  PALETA DE CORES
# ─────────────────────────────────────────────
BG_DARK      = "#0F1117"
BG_PANEL     = "#161B27"
BG_CARD      = "#1E2535"
BG_INPUT     = "#252D40"
BG_ROW_ALT   = "#1A2030"
ACCENT       = "#4F8EF7"
ACCENT_HOVER = "#3A7AE0"
ACCENT_GREEN = "#3DDC84"
ACCENT_RED   = "#F75F5F"
ACCENT_YEL   = "#F7C948"
TEXT_PRI     = "#EEF1F8"
TEXT_SEC     = "#8A94AB"
TEXT_MUT     = "#4E5A72"
BORDER       = "#2A3248"
SIDEBAR_W    = 210


# ─────────────────────────────────────────────
#  HELPERS — UI
# ─────────────────────────────────────────────
def styled_btn(parent, text, bg=ACCENT, fg=TEXT_PRI, cmd=None, w=None):
    kw = dict(
        text=text, bg=bg, fg=fg, relief="flat", cursor="hand2",
        font=("Segoe UI", 9, "bold"), bd=0, padx=14, pady=7,
        activebackground=ACCENT_HOVER, activeforeground=TEXT_PRI,
        command=cmd or (lambda: None)
    )
    if w:
        kw["width"] = w
    btn = tk.Button(parent, **kw)
    def on_enter(e):
        btn.config(bg=(ACCENT_HOVER if bg==ACCENT else
                       "#D94F4F" if bg==ACCENT_RED else
                       "#30B870" if bg==ACCENT_GREEN else BG_INPUT))
    def on_leave(e): btn.config(bg=bg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def labeled_entry(parent, label_text, value="", show=None):
    row = tk.Frame(parent, bg=BG_PANEL)
    row.pack(fill="x", padx=24, pady=5)
    tk.Label(row, text=label_text, bg=BG_PANEL, fg=TEXT_SEC,
             font=("Segoe UI", 9)).pack(anchor="w")
    inp = tk.Frame(row, bg=BG_INPUT)
    inp.pack(fill="x", pady=(2, 0))
    kw = dict(bg=BG_INPUT, fg=TEXT_PRI, relief="flat",
              font=("Segoe UI", 10), insertbackground=ACCENT, bd=0)
    if show:
        kw["show"] = show
    e = tk.Entry(inp, **kw)
    e.pack(fill="x", ipady=8, padx=8)
    if value:
        e.insert(0, str(value))
    return e


def build_treeview(parent, columns):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("SC.Treeview",
        background=BG_CARD, foreground=TEXT_PRI,
        fieldbackground=BG_CARD, rowheight=34,
        font=("Segoe UI", 10), borderwidth=0)
    style.configure("SC.Treeview.Heading",
        background=BG_INPUT, foreground=TEXT_SEC,
        font=("Segoe UI", 9, "bold"), relief="flat", borderwidth=0)
    style.map("SC.Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#FFFFFF")])
    style.layout("SC.Treeview", [("SC.Treeview.treearea", {"sticky": "nswe"})])
    frame = tk.Frame(parent, bg=BG_CARD)
    tv = ttk.Treeview(frame, columns=columns, show="headings",
                      style="SC.Treeview", selectmode="browse")
    sb = tk.Scrollbar(frame, orient="vertical", command=tv.yview,
                      bg=BG_INPUT, troughcolor=BG_CARD,
                      activebackground=ACCENT, width=8, relief="flat")
    tv.configure(yscrollcommand=sb.set)
    tv.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    tv.tag_configure("alt", background=BG_ROW_ALT)
    return frame, tv


def _toast(root, msg, cor=ACCENT_GREEN):
    t = tk.Toplevel(root)
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    t.configure(bg=cor)
    tk.Label(t, text=f"  {msg}  ", bg=cor, fg="#FFFFFF",
             font=("Segoe UI", 10, "bold"), pady=8).pack()
    root.update_idletasks()
    x = root.winfo_x() + root.winfo_width()  - 260
    y = root.winfo_y() + root.winfo_height() - 60
    t.geometry(f"+{x}+{y}")
    t.after(2200, t.destroy)


# ═══════════════════════════════════════════════════════════════════════
#  FORMULÁRIO DE CLIENTE
# ═══════════════════════════════════════════════════════════════════════
class ClienteForm(tk.Toplevel):
    def __init__(self, parent, root_win, on_save, cliente=None):
        super().__init__(parent)
        self.root_win = root_win
        self.on_save  = on_save
        self.cliente  = cliente
        self.title("Novo Cliente" if not cliente else "Editar Cliente")
        self.configure(bg=BG_PANEL)
        self.geometry("460x460")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        c = self.cliente
        editing = c is not None
        tk.Label(self, text="Novo Cliente" if not editing else "Editar Cliente",
                 bg=BG_PANEL, fg=TEXT_PRI,
                 font=("Segoe UI", 15, "bold")).pack(pady=(20,12), padx=24, anchor="w")

        self.e_nome  = labeled_entry(self, "Nome completo *",    c.nome             if c else "")
        self.e_cpf   = labeled_entry(self, "CPF *",              c.cpf              if c else "")
        self.e_tel   = labeled_entry(self, "Telefone",           c.telefone or ""   if c else "")
        self.e_email = labeled_entry(self, "E-mail *",           c.email            if c else "")
        self.e_nasc  = labeled_entry(self, "Data nascimento (AAAA-MM-DD)",
                                           c.data_nascimento or "" if c else "")

        tk.Label(self, text="* campos obrigatórios", bg=BG_PANEL,
                 fg=TEXT_MUT, font=("Segoe UI", 8)).pack(padx=24, anchor="w")

        btns = tk.Frame(self, bg=BG_PANEL)
        btns.pack(fill="x", padx=24, pady=18)
        styled_btn(btns, "Cancelar", bg=BG_CARD, fg=TEXT_SEC, cmd=self.destroy).pack(side="right")
        styled_btn(btns, "💾  Salvar", bg=ACCENT_GREEN, cmd=self._salvar).pack(side="right", padx=(0,8))

    def _salvar(self):
        nome  = self.e_nome.get().strip()
        cpf   = self.e_cpf.get().strip()
        tel   = self.e_tel.get().strip() or None
        email = self.e_email.get().strip()
        nasc  = self.e_nasc.get().strip() or None

        if not nome or not cpf or not email:
            messagebox.showwarning("Atenção", "Nome, CPF e E-mail são obrigatórios.", parent=self)
            return
        try:
            if self.cliente is None:
                novo_id = ClienteDAO.inserir(nome, cpf, tel, email, nasc)
                salvo   = ClienteDAO.buscar_por_id(novo_id)
                _toast(self.root_win, "✓ Cliente cadastrado!")
            else:
                ClienteDAO.alterar(self.cliente.id_cliente, nome, cpf, tel, email, nasc)
                salvo = ClienteDAO.buscar_por_id(self.cliente.id_cliente)
                _toast(self.root_win, "✓ Cliente atualizado!")
            self.on_save(salvo)
            self.destroy()
        except Exception as err:
            messagebox.showerror("Erro no banco de dados", str(err), parent=self)


# ═══════════════════════════════════════════════════════════════════════
#  PÁGINA — CLIENTES
# ═══════════════════════════════════════════════════════════════════════
class ClientesPage(tk.Frame):
    def __init__(self, parent, root_win):
        super().__init__(parent, bg=BG_DARK)
        self.root_win = root_win
        self._build()
        self._recarregar()

    def _build(self):
        hdr = tk.Frame(self, bg=BG_DARK)
        hdr.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(hdr, text="Clientes", bg=BG_DARK,
                 fg=TEXT_PRI, font=("Segoe UI", 20, "bold")).pack(side="left")
        self.lbl_cnt = tk.Label(hdr, text="", bg=BG_DARK,
                                 fg=TEXT_SEC, font=("Segoe UI", 11))
        self.lbl_cnt.pack(side="left", pady=4)
        styled_btn(hdr, "+ Novo Cliente", cmd=self._novo).pack(side="right")

        bar = tk.Frame(self, bg=BG_DARK)
        bar.pack(fill="x", padx=28, pady=12)
        sf = tk.Frame(bar, bg=BG_INPUT)
        sf.pack(side="left", fill="x", expand=True)
        tk.Label(sf, text="🔍", bg=BG_INPUT, fg=TEXT_SEC,
                 font=("Segoe UI", 11)).pack(side="left", padx=8)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)
        tk.Entry(sf, textvariable=self.search_var, bg=BG_INPUT, fg=TEXT_PRI,
                 insertbackground=ACCENT, relief="flat", font=("Segoe UI", 10),
                 bd=0).pack(side="left", fill="x", expand=True, ipady=8)
        styled_btn(bar, "↺ Atualizar", bg=BG_CARD, fg=TEXT_SEC,
                   cmd=self._recarregar, w=12).pack(side="right", padx=3)

        cols = ("ID", "Nome", "CPF", "Telefone", "E-mail", "Nasc.")
        tv_frame, self.tv = build_treeview(self, cols)
        tv_frame.pack(fill="both", expand=True, padx=28, pady=(0, 8))
        for col, w, anch in zip(cols,
                                 (50, 200, 130, 130, 200, 110),
                                 ("center","w","center","center","w","center")):
            self.tv.heading(col, text=col)
            self.tv.column(col, width=w, anchor=anch)

        actions = tk.Frame(self, bg=BG_PANEL)
        actions.pack(fill="x", padx=28, pady=(4, 20))
        styled_btn(actions, "✏  Editar",     bg=ACCENT,       cmd=self._editar).pack(side="left", padx=(0,8))
        styled_btn(actions, "🗑  Excluir",    bg=ACCENT_RED,   cmd=self._excluir).pack(side="left", padx=(0,8))
        styled_btn(actions, "📋  Relatório",  bg=BG_CARD, fg=ACCENT_YEL,
                   cmd=self._relatorio).pack(side="left")

    def _recarregar(self):
        try:
            self._popular(ClienteDAO.listar_todos())
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar clientes:\n{e}")

    def _popular(self, clientes):
        self.tv.delete(*self.tv.get_children())
        for i, c in enumerate(clientes):
            self.tv.insert("", "end", iid=str(c.id_cliente),
                           values=(c.id_cliente, c.nome, c.cpf,
                                   c.telefone or "—", c.email,
                                   c.data_nascimento or "—"),
                           tags=("alt",) if i % 2 else ())
        n = len(clientes)
        self.lbl_cnt.config(text=f"  {n} registro{'s' if n != 1 else ''}")

    def _on_search(self, *_):
        q = self.search_var.get().strip()
        if not q:
            self._recarregar(); return
        try:
            self._popular(ClienteDAO.pesquisar_por_nome(q))
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _novo(self):
        ClienteForm(self, self.root_win, on_save=lambda _: self._recarregar())

    def _get_selecionado(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo("SmartClinic", "Selecione um cliente primeiro.")
            return None
        try:
            return ClienteDAO.buscar_por_id(int(sel[0]))
        except Exception as e:
            messagebox.showerror("Erro", str(e)); return None

    def _editar(self):
        c = self._get_selecionado()
        if c:
            ClienteForm(self, self.root_win, cliente=c,
                        on_save=lambda _: self._recarregar())

    def _excluir(self):
        c = self._get_selecionado()
        if not c: return
        if messagebox.askyesno("Confirmar exclusão",
                               f"Excluir '{c.nome}'?\n\nEsta ação não pode ser desfeita.",
                               icon="warning"):
            try:
                ClienteDAO.remover(c.id_cliente)
                _toast(self.root_win, "✓ Cliente removido.", ACCENT_RED)
                self._recarregar()
            except Exception as e:
                messagebox.showerror("Erro ao excluir", str(e))

    def _relatorio(self):
        try:
            r = ClienteDAO.gerar_relatorio()
        except Exception as e:
            messagebox.showerror("Erro", str(e)); return

        win = tk.Toplevel(self)
        win.title("Relatório de Clientes")
        win.configure(bg=BG_PANEL)
        win.geometry("340x260")
        win.resizable(False, False)
        win.grab_set()
        tk.Label(win, text="📋  Relatório do Sistema", bg=BG_PANEL, fg=TEXT_PRI,
                 font=("Segoe UI", 14, "bold")).pack(pady=(20,12), padx=24, anchor="w")
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=24)
        for lbl, val, cor in [
            ("Total de clientes",      r["total_clientes"],        ACCENT),
            ("Com telefone",           r["clientes_com_telefone"], ACCENT_GREEN),
            ("Com e-mail",             r["clientes_com_email"],    ACCENT_YEL),
        ]:
            row = tk.Frame(win, bg=BG_PANEL)
            row.pack(fill="x", padx=28, pady=8)
            tk.Label(row, text=lbl, bg=BG_PANEL, fg=TEXT_SEC,
                     font=("Segoe UI", 10)).pack(side="left")
            tk.Label(row, text=str(val), bg=BG_PANEL, fg=cor,
                     font=("Segoe UI", 14, "bold")).pack(side="right")
        styled_btn(win, "Fechar", cmd=win.destroy).pack(pady=16)


# ═══════════════════════════════════════════════════════════════════════
#  PÁGINA — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
class DashboardPage(tk.Frame):
    def __init__(self, parent, root_win):
        super().__init__(parent, bg=BG_DARK)
        self.root_win = root_win
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=BG_DARK)
        hdr.pack(fill="x", padx=28, pady=(28, 4))
        tk.Label(hdr, text="Painel Geral", bg=BG_DARK, fg=TEXT_PRI,
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        styled_btn(hdr, "↺ Atualizar", bg=BG_CARD, fg=TEXT_SEC,
                   cmd=self._atualizar, w=12).pack(side="right")

        self.kpis_frame = tk.Frame(self, bg=BG_DARK)
        self.kpis_frame.pack(fill="x", padx=28, pady=(16, 20))
        self.kpi_widgets = {}
        for icon, title, clr in [
            ("👥", "Clientes",      ACCENT),
            ("📞", "Com Telefone",  ACCENT_YEL),
            ("📧", "Com E-mail",    ACCENT_GREEN),
            ("🗄️", "Banco de Dados", ACCENT_GREEN if DB_DISPONIVEL else ACCENT_RED),
        ]:
            card = tk.Frame(self.kpis_frame, bg=BG_CARD, pady=16, padx=20)
            card.pack(side="left", fill="x", expand=True, padx=(0,12))
            top = tk.Frame(card, bg=BG_CARD)
            top.pack(fill="x")
            tk.Label(top, text=icon,  bg=BG_CARD, fg=clr,     font=("Segoe UI", 18)).pack(side="left")
            tk.Label(top, text=title, bg=BG_CARD, fg=TEXT_SEC, font=("Segoe UI", 9)).pack(side="left", padx=6, pady=4)
            lbl = tk.Label(card, text="—", bg=BG_CARD, fg=TEXT_PRI,
                           font=("Segoe UI", 22, "bold"))
            lbl.pack(anchor="w")
            self.kpi_widgets[title] = (lbl, clr)

        mid = tk.Frame(self, bg=BG_DARK)
        mid.pack(fill="both", expand=True, padx=28, pady=(0,20))

        left = tk.Frame(mid, bg=BG_CARD)
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text="Clientes Recentes", bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 12, "bold"), pady=14).pack(anchor="w", padx=16)
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x")
        self.recentes_frame = tk.Frame(left, bg=BG_CARD)
        self.recentes_frame.pack(fill="both", expand=True)

        right = tk.Frame(mid, bg=BG_CARD, width=280)
        right.pack(side="right", fill="y", padx=(12,0))
        right.pack_propagate(False)
        tk.Label(right, text="Conexão MySQL", bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 11, "bold"), pady=14).pack(anchor="w", padx=16)
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x")
        sc = ACCENT_GREEN if DB_DISPONIVEL else ACCENT_RED
        st = "✓  Conectado"  if DB_DISPONIVEL else "✗  Sem conexão"
        tk.Label(right, text=st, bg=BG_CARD, fg=sc,
                 font=("Segoe UI", 11, "bold"), pady=12).pack(padx=16, anchor="w")
        for k, v in [("Driver","mysql-connector-python"),
                      ("Env","secreto.env"),
                      ("Padrão","DAO Pattern"),
                      ("Status","Online" if DB_DISPONIVEL else "Offline")]:
            r = tk.Frame(right, bg=BG_CARD)
            r.pack(fill="x", padx=16, pady=3)
            tk.Label(r, text=k, bg=BG_CARD, fg=TEXT_MUT, font=("Segoe UI", 9)).pack(side="left")
            tk.Label(r, text=v, bg=BG_CARD, fg=TEXT_SEC, font=("Segoe UI", 9)).pack(side="right")

        self._atualizar()

    def _atualizar(self):
        try:
            rel      = ClienteDAO.gerar_relatorio()
            clientes = ClienteDAO.listar_todos()
            for title, val in [("Clientes",     str(rel["total_clientes"])),
                                 ("Com Telefone", str(rel["clientes_com_telefone"])),
                                 ("Com E-mail",   str(rel["clientes_com_email"])),
                                 ("Banco de Dados", "OK")]:
                lbl, clr = self.kpi_widgets[title]
                lbl.config(text=val, fg=clr)
            for w in self.recentes_frame.winfo_children():
                w.destroy()
            if not clientes:
                tk.Label(self.recentes_frame, text="Nenhum cliente cadastrado.",
                         bg=BG_CARD, fg=TEXT_MUT,
                         font=("Segoe UI", 10)).pack(pady=20)
            else:
                for c in list(reversed(clientes))[:6]:
                    r = tk.Frame(self.recentes_frame, bg=BG_CARD)
                    r.pack(fill="x", padx=16, pady=6)
                    tk.Label(r, text=c.nome,  bg=BG_CARD, fg=TEXT_PRI, font=("Segoe UI", 10)).pack(side="left")
                    tk.Label(r, text=c.email, bg=BG_CARD, fg=TEXT_MUT, font=("Segoe UI", 9)).pack(side="right")
        except Exception:
            for _, (lbl, _) in self.kpi_widgets.items():
                lbl.config(text="ERR", fg=ACCENT_RED)


# ═══════════════════════════════════════════════════════════════════════
#  TELA DE ERRO DE CONEXÃO
# ═══════════════════════════════════════════════════════════════════════
class ConexaoErroPage(tk.Frame):
    def __init__(self, parent, msg_erro):
        super().__init__(parent, bg=BG_DARK)
        tk.Label(self, text="⚠", bg=BG_DARK, fg=ACCENT_RED,
                 font=("Segoe UI", 48)).pack(pady=(60,8))
        tk.Label(self, text="Não foi possível conectar ao banco de dados",
                 bg=BG_DARK, fg=TEXT_PRI,
                 font=("Segoe UI", 15, "bold")).pack()
        tk.Label(self, text=msg_erro, bg=BG_DARK, fg=TEXT_SEC,
                 font=("Segoe UI", 10), wraplength=520).pack(pady=12)
        tk.Label(self,
                 text="Verifique se o MySQL está rodando e se o arquivo secreto.env existe\n"
                      "na raiz do projeto com: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME",
                 bg=BG_DARK, fg=TEXT_MUT, font=("Segoe UI", 9), wraplength=520).pack()


# ═══════════════════════════════════════════════════════════════════════
#  APLICAÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════
class SmartClinic:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SmartClinic — Sistema Integrado de Gestão Clínica")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1100x680")
        self.root.minsize(900, 600)
        self._build_layout()
        self.root.mainloop()

    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=BG_PANEL, width=SIDEBAR_W)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        lf = tk.Frame(self.sidebar, bg=BG_PANEL, pady=22)
        lf.pack(fill="x")
        tk.Label(lf, text="⚕",           bg=BG_PANEL, fg=ACCENT,   font=("Segoe UI", 24)).pack()
        tk.Label(lf, text="SmartClinic", bg=BG_PANEL, fg=TEXT_PRI,  font=("Segoe UI", 13, "bold")).pack()
        tk.Label(lf, text="Gestão Clínica v2.0", bg=BG_PANEL, fg=TEXT_MUT, font=("Segoe UI", 8)).pack()
        clr_badge = ACCENT_GREEN if DB_DISPONIVEL else ACCENT_RED
        txt_badge = "● MySQL Conectado" if DB_DISPONIVEL else "● Sem Conexão"
        tk.Label(lf, text=txt_badge, bg=BG_PANEL, fg=clr_badge, font=("Segoe UI", 8)).pack(pady=(4,0))

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=4)

        self.nav_items   = {}
        self.active_page = None

        if DB_DISPONIVEL:
            menu = [
                ("📊", "Dashboard", lambda p: DashboardPage(p, self.root)),
                ("👥", "Clientes",  lambda p: ClientesPage(p,  self.root)),
            ]
        else:
            menu = [("⚠", "Conexão", lambda p: ConexaoErroPage(p, _DB_ERRO_MSG))]

        for icon, label, _ in menu:
            self._add_nav_item(icon, label)

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=12)
        bottom = tk.Frame(self.sidebar, bg=BG_PANEL)
        bottom.pack(side="bottom", fill="x", pady=12)
        tk.Label(bottom, text="SmartClinic © 2026", bg=BG_PANEL,
                 fg=TEXT_MUT, font=("Segoe UI", 7)).pack()

        # Área principal
        self.main_area = tk.Frame(self.root, bg=BG_DARK)
        self.main_area.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(self.main_area, bg=BG_PANEL, height=48)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        self.topbar_title = tk.Label(topbar, text="", bg=BG_PANEL,
                                      fg=TEXT_PRI, font=("Segoe UI", 11, "bold"))
        self.topbar_title.pack(side="left", padx=20, pady=12)
        tk.Label(topbar, text="Admin  ▾", bg=BG_PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(side="right", padx=20)
        tk.Label(topbar, text="🔔", bg=BG_PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 12)).pack(side="right")

        self.content = tk.Frame(self.main_area, bg=BG_DARK)
        self.content.pack(fill="both", expand=True)

        self.pages = {}
        for _, label, factory in menu:
            page = factory(self.content)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[label] = page

        self._switch(list(self.pages.keys())[0])

    def _add_nav_item(self, icon, label):
        btn_frame = tk.Frame(self.sidebar, bg=BG_PANEL, cursor="hand2")
        btn_frame.pack(fill="x", padx=10, pady=2)
        accent_bar = tk.Frame(btn_frame, bg=BG_PANEL, width=3)
        accent_bar.pack(side="left", fill="y")
        inner = tk.Frame(btn_frame, bg=BG_PANEL, padx=10, pady=10)
        inner.pack(fill="x", side="left")
        icon_lbl = tk.Label(inner, text=icon, bg=BG_PANEL, fg=TEXT_SEC, font=("Segoe UI", 13))
        icon_lbl.pack(side="left")
        lbl = tk.Label(inner, text=label, bg=BG_PANEL, fg=TEXT_SEC, font=("Segoe UI", 10))
        lbl.pack(side="left", padx=10)
        widgets = (btn_frame, inner, icon_lbl, lbl, accent_bar)

        def on_enter(e, ww=widgets):
            if self.active_page != label:
                for w in ww: w.config(bg="#1C2236")
        def on_leave(e, ww=widgets):
            if self.active_page != label:
                for w in ww: w.config(bg=BG_PANEL)
        for w in widgets:
            w.bind("<Button-1>", lambda e, l=label: self._switch(l))
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
        self.nav_items[label] = (widgets, accent_bar)

    def _switch(self, name):
        if self.active_page and self.active_page in self.nav_items:
            pw, pb = self.nav_items[self.active_page]
            for w in pw: w.config(bg=BG_PANEL)
            pb.config(bg=BG_PANEL)
            pw[2].config(fg=TEXT_SEC); pw[3].config(fg=TEXT_SEC)
        self.active_page = name
        widgets, bar = self.nav_items[name]
        for w in widgets: w.config(bg="#1C2A45")
        bar.config(bg=ACCENT, width=3)
        widgets[2].config(fg=ACCENT); widgets[3].config(fg=TEXT_PRI)
        self.pages[name].lift()
        self.topbar_title.config(text=name)


if __name__ == "__main__":
    SmartClinic()