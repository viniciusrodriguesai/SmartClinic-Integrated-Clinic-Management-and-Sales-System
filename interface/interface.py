"""
SmartClinic — Interface Completa (Parte 2)
Clientes · Vendedores · Produtos · Compras · Relatórios
"""
import sys, os, datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC_DIR))

DB_DISPONIVEL = False
_DB_ERRO_MSG  = ""
try:
    from cliente_dao  import ClienteDAO,  Cliente
    from vendedor_dao import VendedorDAO, Vendedor
    from produto_dao  import ProdutoDAO,  Produto
    from compra_dao   import CompraDAO,   Compra, ItemCompra
    from db import get_conn
    with get_conn() as _c: pass
    DB_DISPONIVEL = True
except Exception as _e:
    _DB_ERRO_MSG = str(_e)

# ── Cores ────────────────────────────────────────────────────
BG_DARK=  "#0F1117"; BG_PANEL= "#161B27"; BG_CARD=  "#1E2535"
BG_INPUT= "#252D40"; BG_ROW_ALT="#1A2030"
ACCENT=   "#4F8EF7"; ACCENT_HOVER="#3A7AE0"
ACCENT_GREEN="#3DDC84"; ACCENT_RED="#F75F5F"; ACCENT_YEL="#F7C948"
TEXT_PRI= "#EEF1F8"; TEXT_SEC= "#8A94AB";  TEXT_MUT= "#4E5A72"
BORDER=   "#2A3248"; SIDEBAR_W=210

# ── Helpers UI ───────────────────────────────────────────────
def styled_btn(parent, text, bg=ACCENT, fg=TEXT_PRI, cmd=None, w=None):
    kw = dict(text=text, bg=bg, fg=fg, relief="flat", cursor="hand2",
              font=("Segoe UI",9,"bold"), bd=0, padx=14, pady=7,
              activebackground=ACCENT_HOVER, activeforeground=TEXT_PRI,
              command=cmd or (lambda: None))
    if w: kw["width"] = w
    btn = tk.Button(parent, **kw)
    def on_enter(e): btn.config(bg=(ACCENT_HOVER if bg==ACCENT else "#D94F4F" if bg==ACCENT_RED else "#30B870" if bg==ACCENT_GREEN else BG_INPUT))
    def on_leave(e): btn.config(bg=bg)
    btn.bind("<Enter>",on_enter); btn.bind("<Leave>",on_leave)
    return btn

def labeled_entry(parent, label, value="", show=None):
    f = tk.Frame(parent, bg=BG_PANEL); f.pack(fill="x", padx=24, pady=4)
    tk.Label(f, text=label, bg=BG_PANEL, fg=TEXT_SEC, font=("Segoe UI",9)).pack(anchor="w")
    inp = tk.Frame(f, bg=BG_INPUT); inp.pack(fill="x", pady=(2,0))
    kw = dict(bg=BG_INPUT,fg=TEXT_PRI,relief="flat",font=("Segoe UI",10),insertbackground=ACCENT,bd=0)
    if show: kw["show"]=show
    e = tk.Entry(inp, **kw); e.pack(fill="x", ipady=8, padx=8)
    if value: e.insert(0, str(value))
    return e

def labeled_combo(parent, label, values, current=""):
    f = tk.Frame(parent, bg=BG_PANEL); f.pack(fill="x", padx=24, pady=4)
    tk.Label(f, text=label, bg=BG_PANEL, fg=TEXT_SEC, font=("Segoe UI",9)).pack(anchor="w")
    v = tk.StringVar(value=current)
    style = ttk.Style(); style.configure("SC.TCombobox", fieldbackground=BG_INPUT, background=BG_INPUT, foreground=TEXT_PRI)
    cb = ttk.Combobox(f, textvariable=v, values=values, state="readonly", font=("Segoe UI",10))
    cb.pack(fill="x", pady=(2,0), ipady=4)
    return cb, v

def labeled_check(parent, label, value=False):
    f = tk.Frame(parent, bg=BG_PANEL); f.pack(fill="x", padx=24, pady=4)
    v = tk.BooleanVar(value=value)
    tk.Checkbutton(f, text=label, variable=v, bg=BG_PANEL, fg=TEXT_PRI,
                   selectcolor=BG_INPUT, activebackground=BG_PANEL,
                   font=("Segoe UI",10)).pack(anchor="w")
    return v

def build_treeview(parent, columns):
    style = ttk.Style(); style.theme_use("clam")
    style.configure("SC.Treeview", background=BG_CARD, foreground=TEXT_PRI,
        fieldbackground=BG_CARD, rowheight=32, font=("Segoe UI",10), borderwidth=0)
    style.configure("SC.Treeview.Heading", background=BG_INPUT, foreground=TEXT_SEC,
        font=("Segoe UI",9,"bold"), relief="flat", borderwidth=0)
    style.map("SC.Treeview", background=[("selected",ACCENT)], foreground=[("selected","#FFF")])
    style.layout("SC.Treeview",[("SC.Treeview.treearea",{"sticky":"nswe"})])
    frame = tk.Frame(parent, bg=BG_CARD)
    tv = ttk.Treeview(frame, columns=columns, show="headings", style="SC.Treeview", selectmode="browse")
    sb = tk.Scrollbar(frame, orient="vertical", command=tv.yview, bg=BG_INPUT,
                      troughcolor=BG_CARD, activebackground=ACCENT, width=8, relief="flat")
    tv.configure(yscrollcommand=sb.set)
    tv.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
    tv.tag_configure("alt", background=BG_ROW_ALT)
    tv.tag_configure("pendente", foreground=ACCENT_YEL)
    tv.tag_configure("confirmado", foreground=ACCENT_GREEN)
    tv.tag_configure("baixo", foreground=ACCENT_RED)
    tv.tag_configure("desc", foreground=ACCENT_YEL)
    return frame, tv

def _toast(root, msg, cor=ACCENT_GREEN):
    t = tk.Toplevel(root); t.overrideredirect(True); t.attributes("-topmost",True); t.configure(bg=cor)
    tk.Label(t,text=f"  {msg}  ",bg=cor,fg="#FFF",font=("Segoe UI",10,"bold"),pady=8).pack()
    root.update_idletasks()
    t.geometry(f"+{root.winfo_x()+root.winfo_width()-260}+{root.winfo_y()+root.winfo_height()-60}")
    t.after(2200, t.destroy)

def section_header(parent, title):
    hdr = tk.Frame(parent, bg=BG_DARK)
    hdr.pack(fill="x", padx=28, pady=(24,0))
    tk.Label(hdr, text=title, bg=BG_DARK, fg=TEXT_PRI, font=("Segoe UI",20,"bold")).pack(side="left")
    return hdr

# ════════════════════════════════════════════════════════════════
#  PÁGINA — DASHBOARD
# ════════════════════════════════════════════════════════════════
class DashboardPage(tk.Frame):
    def __init__(self, parent, root_win):
        super().__init__(parent, bg=BG_DARK)
        self.root_win = root_win; self._build()

    def _build(self):
        hdr = section_header(self, "Painel Geral")
        styled_btn(hdr,"↺ Atualizar",bg=BG_CARD,fg=TEXT_SEC,cmd=self._atualizar,w=12).pack(side="right")

        self.kpis = tk.Frame(self,bg=BG_DARK); self.kpis.pack(fill="x",padx=28,pady=(16,20))
        self.kpi_lbls = {}
        for icon,title,clr in [("👥","Clientes",ACCENT),("👨‍⚕️","Vendedores",ACCENT_YEL),
                                 ("📦","Produtos",ACCENT_GREEN),("💳","Compras",ACCENT_RED)]:
            card = tk.Frame(self.kpis,bg=BG_CARD,pady=16,padx=20); card.pack(side="left",fill="x",expand=True,padx=(0,12))
            top = tk.Frame(card,bg=BG_CARD); top.pack(fill="x")
            tk.Label(top,text=icon,bg=BG_CARD,fg=clr,font=("Segoe UI",18)).pack(side="left")
            tk.Label(top,text=title,bg=BG_CARD,fg=TEXT_SEC,font=("Segoe UI",9)).pack(side="left",padx=6)
            lbl = tk.Label(card,text="—",bg=BG_CARD,fg=TEXT_PRI,font=("Segoe UI",22,"bold")); lbl.pack(anchor="w")
            self.kpi_lbls[title] = (lbl, clr)

        mid = tk.Frame(self,bg=BG_DARK); mid.pack(fill="both",expand=True,padx=28,pady=(0,20))

        left = tk.Frame(mid,bg=BG_CARD); left.pack(side="left",fill="both",expand=True,padx=(0,12))
        tk.Label(left,text="⚠  Estoque Baixo (< 5 unidades)",bg=BG_CARD,fg=ACCENT_RED,
                 font=("Segoe UI",11,"bold"),pady=12).pack(anchor="w",padx=16)
        tk.Frame(left,bg=BORDER,height=1).pack(fill="x")
        self.estoque_frame = tk.Frame(left,bg=BG_CARD); self.estoque_frame.pack(fill="both",expand=True)

        right = tk.Frame(mid,bg=BG_CARD,width=300); right.pack(side="right",fill="y"); right.pack_propagate(False)
        tk.Label(right,text="💳  Últimas Compras",bg=BG_CARD,fg=TEXT_PRI,
                 font=("Segoe UI",11,"bold"),pady=12).pack(anchor="w",padx=16)
        tk.Frame(right,bg=BORDER,height=1).pack(fill="x")
        self.ultimas_frame = tk.Frame(right,bg=BG_CARD); self.ultimas_frame.pack(fill="both",expand=True)

        self._atualizar()

    def _atualizar(self):
        try:
            rc = ClienteDAO.gerar_relatorio(); rp = ProdutoDAO.gerar_relatorio(); rc2 = CompraDAO.gerar_relatorio_geral()
            vs = VendedorDAO.listar_todos(); compras = CompraDAO.listar_todas()
            baixo = ProdutoDAO.pesquisar(estoque_baixo=True)

            for t,v in [("Clientes",str(rc["total_clientes"])),("Vendedores",str(len(vs))),
                        ("Produtos",str(rp["total_produtos"])),("Compras",str(rc2["total_compras"]))]:
                lbl,clr = self.kpi_lbls[t]; lbl.config(text=v, fg=clr)

            for w in self.estoque_frame.winfo_children(): w.destroy()
            if not baixo:
                tk.Label(self.estoque_frame,text="Nenhum produto com estoque baixo ✓",bg=BG_CARD,
                         fg=ACCENT_GREEN,font=("Segoe UI",10)).pack(pady=16)
            else:
                for p in baixo:
                    r = tk.Frame(self.estoque_frame,bg=BG_CARD); r.pack(fill="x",padx=16,pady=5)
                    tk.Label(r,text=p.nome,bg=BG_CARD,fg=TEXT_PRI,font=("Segoe UI",10)).pack(side="left")
                    clr = ACCENT_RED if p.quantidade == 0 else ACCENT_YEL
                    tk.Label(r,text=f"{p.quantidade} un.",bg=BG_CARD,fg=clr,font=("Segoe UI",10,"bold")).pack(side="right")

            for w in self.ultimas_frame.winfo_children(): w.destroy()
            for c in compras[:6]:
                r = tk.Frame(self.ultimas_frame,bg=BG_CARD); r.pack(fill="x",padx=16,pady=5)
                tk.Label(r,text=c.nome_cliente,bg=BG_CARD,fg=TEXT_PRI,font=("Segoe UI",9)).pack(side="left")
                clr = ACCENT_GREEN if c.status_pagamento=="confirmado" else ACCENT_YEL
                tk.Label(r,text=f"R$ {c.valor_total:.2f}",bg=BG_CARD,fg=clr,font=("Segoe UI",9,"bold")).pack(side="right")
        except Exception as e:
            for _,(lbl,_) in self.kpi_lbls.items(): lbl.config(text="ERR",fg=ACCENT_RED)

# ════════════════════════════════════════════════════════════════
#  PÁGINA — CLIENTES
# ════════════════════════════════════════════════════════════════
class ClientesPage(tk.Frame):
    def __init__(self, parent, root_win):
        super().__init__(parent, bg=BG_DARK); self.root_win=root_win; self._build(); self._reload()

    def _build(self):
        hdr = section_header(self,"Clientes")
        self.lbl_cnt = tk.Label(hdr,text="",bg=BG_DARK,fg=TEXT_SEC,font=("Segoe UI",11)); self.lbl_cnt.pack(side="left",pady=4)
        styled_btn(hdr,"+ Novo",cmd=self._novo).pack(side="right")

        bar = tk.Frame(self,bg=BG_DARK); bar.pack(fill="x",padx=28,pady=10)
        sf = tk.Frame(bar,bg=BG_INPUT); sf.pack(side="left",fill="x",expand=True)
        tk.Label(sf,text="🔍",bg=BG_INPUT,fg=TEXT_SEC,font=("Segoe UI",11)).pack(side="left",padx=8)
        self.sv = tk.StringVar(); self.sv.trace("w",self._search)
        tk.Entry(sf,textvariable=self.sv,bg=BG_INPUT,fg=TEXT_PRI,insertbackground=ACCENT,
                 relief="flat",font=("Segoe UI",10),bd=0).pack(side="left",fill="x",expand=True,ipady=8)
        styled_btn(bar,"↺",bg=BG_CARD,fg=TEXT_SEC,cmd=self._reload,w=3).pack(side="right",padx=3)

        cols=("ID","Nome","CPF","Cidade","Telefone","E-mail","Desconto")
        frm,self.tv = build_treeview(self,cols); frm.pack(fill="both",expand=True,padx=28,pady=(0,8))
        for col,w,a in zip(cols,(50,180,130,90,120,180,80),("center","w","center","center","center","w","center")):
            self.tv.heading(col,text=col); self.tv.column(col,width=w,anchor=a)

        act = tk.Frame(self,bg=BG_PANEL); act.pack(fill="x",padx=28,pady=(4,20))
        styled_btn(act,"✏ Editar",bg=ACCENT,cmd=self._edit).pack(side="left",padx=(0,8))
        styled_btn(act,"🗑 Excluir",bg=ACCENT_RED,cmd=self._delete).pack(side="left",padx=(0,8))
        styled_btn(act,"📋 Relatório",bg=BG_CARD,fg=ACCENT_YEL,cmd=self._relatorio).pack(side="left")

    def _reload(self):
        try: self._populate(ClienteDAO.listar_todos())
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _populate(self, lst):
        self.tv.delete(*self.tv.get_children())
        for i,c in enumerate(lst):
            desc = "✓ 10%" if c.tem_desconto else "—"
            tag = ("desc","alt")[i%2] if c.tem_desconto else ("","alt")[i%2]
            self.tv.insert("","end",iid=str(c.id_cliente),
                           values=(c.id_cliente,c.nome,c.cpf,c.cidade or "—",
                                   c.telefone or "—",c.email,desc),tags=(tag,))
        n=len(lst); self.lbl_cnt.config(text=f"  {n} registro{'s'if n!=1 else''}")

    def _search(self,*_):
        q=self.sv.get().strip()
        try: self._populate(ClienteDAO.pesquisar_por_nome(q) if q else ClienteDAO.listar_todos())
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _novo(self): ClienteForm(self,self.root_win,on_save=lambda _:self._reload())
    def _sel(self):
        s=self.tv.selection()
        if not s: messagebox.showinfo("SmartClinic","Selecione um cliente."); return None
        try: return ClienteDAO.buscar_por_id(int(s[0]))
        except Exception as e: messagebox.showerror("Erro",str(e)); return None
    def _edit(self):
        c=self._sel()
        if c: ClienteForm(self,self.root_win,cliente=c,on_save=lambda _:self._reload())
    def _delete(self):
        c=self._sel()
        if not c: return
        if messagebox.askyesno("Confirmar",f"Excluir '{c.nome}'?",icon="warning"):
            try: ClienteDAO.remover(c.id_cliente); _toast(self.root_win,"✓ Cliente removido.",ACCENT_RED); self._reload()
            except Exception as e: messagebox.showerror("Erro",str(e))

    def _relatorio(self):
        try: r=ClienteDAO.gerar_relatorio()
        except Exception as e: messagebox.showerror("Erro",str(e)); return
        win=tk.Toplevel(self); win.title("Relatório de Clientes"); win.configure(bg=BG_PANEL)
        win.geometry("360x320"); win.resizable(False,False); win.grab_set()
        tk.Label(win,text="📋 Relatório de Clientes",bg=BG_PANEL,fg=TEXT_PRI,
                 font=("Segoe UI",14,"bold")).pack(pady=(20,10),padx=24,anchor="w")
        tk.Frame(win,bg=BORDER,height=1).pack(fill="x",padx=24)
        for lbl,val,cor in [("Total de clientes",r["total_clientes"],ACCENT),
                             ("Com telefone",r["clientes_com_telefone"],ACCENT_GREEN),
                             ("Com e-mail",r["clientes_com_email"],ACCENT_GREEN),
                             ("Torcem pro Flamengo 🔴⚫",r["torcem_flamengo"],ACCENT_RED),
                             ("Assistem One Piece 🏴‍☠️",r["assistem_one_piece"],ACCENT_YEL),
                             ("São de Sousa 📍",r["de_sousa"],ACCENT)]:
            row=tk.Frame(win,bg=BG_PANEL); row.pack(fill="x",padx=28,pady=5)
            tk.Label(row,text=lbl,bg=BG_PANEL,fg=TEXT_SEC,font=("Segoe UI",10)).pack(side="left")
            tk.Label(row,text=str(val),bg=BG_PANEL,fg=cor,font=("Segoe UI",13,"bold")).pack(side="right")
        styled_btn(win,"Fechar",cmd=win.destroy).pack(pady=14)

class ClienteForm(tk.Toplevel):
    def __init__(self, parent, root_win, on_save, cliente=None):
        super().__init__(parent); self.root_win=root_win; self.on_save=on_save; self.cliente=cliente
        self.title("Novo Cliente" if not cliente else "Editar Cliente")
        self.configure(bg=BG_PANEL); self.geometry("480x620"); self.resizable(False,False); self.grab_set()
        c=cliente
        tk.Label(self,text="Novo Cliente" if not c else "Editar Cliente",
                 bg=BG_PANEL,fg=TEXT_PRI,font=("Segoe UI",15,"bold")).pack(pady=(20,4),padx=24,anchor="w")
        tk.Frame(self,bg=BORDER,height=1).pack(fill="x",padx=24,pady=(0,6))
        self.e_nome  = labeled_entry(self,"Nome completo *",   c.nome           if c else "")
        self.e_cpf   = labeled_entry(self,"CPF *",             c.cpf            if c else "")
        self.e_tel   = labeled_entry(self,"Telefone",          c.telefone or "" if c else "")
        self.e_email = labeled_entry(self,"E-mail *",          c.email          if c else "")
        self.e_nasc  = labeled_entry(self,"Nascimento (AAAA-MM-DD)", c.data_nascimento or "" if c else "")
        self.e_cid   = labeled_entry(self,"Cidade",            c.cidade or ""   if c else "")
        self.v_flam  = labeled_check(self,"❤️  Torce pro Flamengo (10% desconto)", c.torce_flamengo if c else False)
        self.v_op    = labeled_check(self,"🏴‍☠️  Assiste One Piece (10% desconto)", c.assiste_one_piece if c else False)
        tk.Label(self,text="* obrigatórios  |  Cidade 'Sousa' também garante 10% de desconto",
                 bg=BG_PANEL,fg=TEXT_MUT,font=("Segoe UI",8),wraplength=420).pack(padx=24,anchor="w",pady=4)
        tk.Frame(self,bg=BORDER,height=1).pack(fill="x",padx=24,pady=(8,0))
        btns=tk.Frame(self,bg=BG_PANEL); btns.pack(fill="x",padx=24,pady=14)
        styled_btn(btns,"✕ Cancelar",bg=BG_CARD,fg=TEXT_SEC,cmd=self.destroy).pack(side="left")
        styled_btn(btns,"✔ Adicionar Cliente" if not c else "✔ Salvar",bg=ACCENT_GREEN,cmd=self._salvar).pack(side="right")

    def _salvar(self):
        nome=self.e_nome.get().strip(); cpf=self.e_cpf.get().strip()
        tel=self.e_tel.get().strip() or None; email=self.e_email.get().strip()
        nasc=self.e_nasc.get().strip() or None; cid=self.e_cid.get().strip() or None
        flam=self.v_flam.get(); op=self.v_op.get()
        if not nome or not cpf or not email:
            messagebox.showwarning("Atenção","Nome, CPF e E-mail são obrigatórios.",parent=self); return
        try:
            if not self.cliente:
                nid=ClienteDAO.inserir(nome,cpf,tel,email,nasc,cid,flam,op)
                salvo=ClienteDAO.buscar_por_id(nid); _toast(self.root_win,"✓ Cliente cadastrado!")
            else:
                ClienteDAO.alterar(self.cliente.id_cliente,nome,cpf,tel,email,nasc,cid,flam,op)
                salvo=ClienteDAO.buscar_por_id(self.cliente.id_cliente); _toast(self.root_win,"✓ Cliente atualizado!")
            self.on_save(salvo); self.destroy()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self)

# ════════════════════════════════════════════════════════════════
#  PÁGINA — VENDEDORES
# ════════════════════════════════════════════════════════════════
class VendedoresPage(tk.Frame):
    def __init__(self, parent, root_win):
        super().__init__(parent, bg=BG_DARK); self.root_win=root_win; self._build(); self._reload()

    def _build(self):
        hdr=section_header(self,"Vendedores")
        self.lbl_cnt=tk.Label(hdr,text="",bg=BG_DARK,fg=TEXT_SEC,font=("Segoe UI",11)); self.lbl_cnt.pack(side="left",pady=4)
        styled_btn(hdr,"+ Novo",cmd=self._novo).pack(side="right")
        cols=("ID","Nome","CPF","E-mail","Telefone")
        frm,self.tv=build_treeview(self,cols); frm.pack(fill="both",expand=True,padx=28,pady=20)
        for col,w,a in zip(cols,(50,200,130,200,120),("center","w","center","w","center")):
            self.tv.heading(col,text=col); self.tv.column(col,width=w,anchor=a)
        act=tk.Frame(self,bg=BG_PANEL); act.pack(fill="x",padx=28,pady=(0,20))
        styled_btn(act,"✏ Editar",bg=ACCENT,cmd=self._edit).pack(side="left",padx=(0,8))
        styled_btn(act,"🗑 Excluir",bg=ACCENT_RED,cmd=self._delete).pack(side="left",padx=(0,8))
        styled_btn(act,"📊 Rel. Mensal",bg=BG_CARD,fg=ACCENT_YEL,cmd=self._relatorio).pack(side="left")

    def _reload(self):
        try:
            vs=VendedorDAO.listar_todos(); self.tv.delete(*self.tv.get_children())
            for i,v in enumerate(vs):
                self.tv.insert("","end",iid=str(v.id_vendedor),
                               values=(v.id_vendedor,v.nome,v.cpf,v.email,v.telefone or "—"),
                               tags=("alt",) if i%2 else ())
            n=len(vs); self.lbl_cnt.config(text=f"  {n} vendedor{'es'if n!=1 else''}")
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _novo(self): VendedorForm(self,self.root_win,on_save=lambda _:self._reload())
    def _sel(self):
        s=self.tv.selection()
        if not s: messagebox.showinfo("SmartClinic","Selecione um vendedor."); return None
        try: return VendedorDAO.buscar_por_id(int(s[0]))
        except Exception as e: messagebox.showerror("Erro",str(e)); return None
    def _edit(self):
        v=self._sel()
        if v: VendedorForm(self,self.root_win,vendedor=v,on_save=lambda _:self._reload())
    def _delete(self):
        v=self._sel()
        if not v: return
        if messagebox.askyesno("Confirmar",f"Excluir '{v.nome}'?",icon="warning"):
            try: VendedorDAO.remover(v.id_vendedor); _toast(self.root_win,"✓ Vendedor removido.",ACCENT_RED); self._reload()
            except Exception as e: messagebox.showerror("Erro",str(e))

    def _relatorio(self):
        hoje=datetime.date.today()
        try: dados=CompraDAO.relatorio_mensal(hoje.year,hoje.month)
        except Exception as e: messagebox.showerror("Erro",str(e)); return
        win=tk.Toplevel(self); win.title("Relatório Mensal por Vendedor")
        win.configure(bg=BG_PANEL); win.geometry("520x420"); win.resizable(False,False); win.grab_set()
        mes_nome=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"][hoje.month-1]
        tk.Label(win,text=f"📊  Relatório — {mes_nome}/{hoje.year}",bg=BG_PANEL,fg=TEXT_PRI,
                 font=("Segoe UI",14,"bold")).pack(pady=(20,10),padx=24,anchor="w")
        tk.Frame(win,bg=BORDER,height=1).pack(fill="x",padx=24)
        cols=("Vendedor","Vendas","Faturamento","Ticket Médio")
        frm,tv=build_treeview(win,cols); frm.pack(fill="both",expand=True,padx=16,pady=12)
        for col,w in zip(cols,(180,70,120,120)):
            tv.heading(col,text=col); tv.column(col,width=w,anchor="center")
        if not dados:
            tv.insert("","end",values=("Sem dados neste mês","—","—","—"))
        else:
            for i,d in enumerate(dados):
                tv.insert("","end",values=(d["vendedor"],d["total_vendas"],
                          f"R$ {d['faturamento']:.2f}",f"R$ {d['ticket_medio']:.2f}"),
                          tags=("alt",) if i%2 else ())
        styled_btn(win,"Fechar",cmd=win.destroy).pack(pady=12)

class VendedorForm(tk.Toplevel):
    def __init__(self, parent, root_win, on_save, vendedor=None):
        super().__init__(parent); self.root_win=root_win; self.on_save=on_save; self.vendedor=vendedor
        self.title("Novo Vendedor" if not vendedor else "Editar Vendedor")
        self.configure(bg=BG_PANEL); self.geometry("460,420".replace(",","x")); self.geometry("460x420")
        self.resizable(False,False); self.grab_set()
        v=vendedor
        tk.Label(self,text="Novo Vendedor" if not v else "Editar Vendedor",
                 bg=BG_PANEL,fg=TEXT_PRI,font=("Segoe UI",15,"bold")).pack(pady=(20,8),padx=24,anchor="w")
        tk.Frame(self,bg=BORDER,height=1).pack(fill="x",padx=24,pady=(0,6))
        self.e_nome =labeled_entry(self,"Nome *",    v.nome         if v else "")
        self.e_cpf  =labeled_entry(self,"CPF *",     v.cpf          if v else "")
        self.e_email=labeled_entry(self,"E-mail *",  v.email        if v else "")
        self.e_tel  =labeled_entry(self,"Telefone",  v.telefone or "" if v else "")
        tk.Frame(self,bg=BORDER,height=1).pack(fill="x",padx=24,pady=(12,0))
        btns=tk.Frame(self,bg=BG_PANEL); btns.pack(fill="x",padx=24,pady=14)
        styled_btn(btns,"✕ Cancelar",bg=BG_CARD,fg=TEXT_SEC,cmd=self.destroy).pack(side="left")
        styled_btn(btns,"✔ Salvar",bg=ACCENT_GREEN,cmd=self._salvar).pack(side="right")

    def _salvar(self):
        nome=self.e_nome.get().strip(); cpf=self.e_cpf.get().strip()
        email=self.e_email.get().strip(); tel=self.e_tel.get().strip() or None
        if not nome or not cpf or not email:
            messagebox.showwarning("Atenção","Nome, CPF e E-mail obrigatórios.",parent=self); return
        try:
            if not self.vendedor:
                nid=VendedorDAO.inserir(nome,cpf,email,tel)
                salvo=VendedorDAO.buscar_por_id(nid); _toast(self.root_win,"✓ Vendedor cadastrado!")
            else:
                VendedorDAO.alterar(self.vendedor.id_vendedor,nome,cpf,email,tel)
                salvo=VendedorDAO.buscar_por_id(self.vendedor.id_vendedor); _toast(self.root_win,"✓ Vendedor atualizado!")
            self.on_save(salvo); self.destroy()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self)

# ════════════════════════════════════════════════════════════════
#  PÁGINA — PRODUTOS
# ════════════════════════════════════════════════════════════════
class ProdutosPage(tk.Frame):
    def __init__(self, parent, root_win):
        super().__init__(parent, bg=BG_DARK); self.root_win=root_win; self._build(); self._reload()

    def _build(self):
        hdr=section_header(self,"Produtos & Estoque")
        self.lbl_cnt=tk.Label(hdr,text="",bg=BG_DARK,fg=TEXT_SEC,font=("Segoe UI",11)); self.lbl_cnt.pack(side="left",pady=4)
        styled_btn(hdr,"+ Novo",cmd=self._novo).pack(side="right")

        bar=tk.Frame(self,bg=BG_DARK); bar.pack(fill="x",padx=28,pady=10)
        sf=tk.Frame(bar,bg=BG_INPUT); sf.pack(side="left",fill="x",expand=True)
        tk.Label(sf,text="🔍",bg=BG_INPUT,fg=TEXT_SEC,font=("Segoe UI",11)).pack(side="left",padx=8)
        self.sv=tk.StringVar(); self.sv.trace("w",self._search)
        tk.Entry(sf,textvariable=self.sv,bg=BG_INPUT,fg=TEXT_PRI,insertbackground=ACCENT,
                 relief="flat",font=("Segoe UI",10),bd=0).pack(side="left",fill="x",expand=True,ipady=8)

        fil=tk.Frame(self,bg=BG_DARK); fil.pack(fill="x",padx=28,pady=(0,8))
        tk.Label(fil,text="Preço de:",bg=BG_DARK,fg=TEXT_SEC,font=("Segoe UI",9)).pack(side="left")
        self.e_pmin=tk.Entry(fil,bg=BG_INPUT,fg=TEXT_PRI,relief="flat",width=8,insertbackground=ACCENT,font=("Segoe UI",9),bd=0)
        self.e_pmin.pack(side="left",ipady=5,padx=4)
        tk.Label(fil,text="até:",bg=BG_DARK,fg=TEXT_SEC,font=("Segoe UI",9)).pack(side="left")
        self.e_pmax=tk.Entry(fil,bg=BG_INPUT,fg=TEXT_PRI,relief="flat",width=8,insertbackground=ACCENT,font=("Segoe UI",9),bd=0)
        self.e_pmax.pack(side="left",ipady=5,padx=4)
        self.v_mari=tk.BooleanVar()
        tk.Checkbutton(fil,text="Fabricado em Mari",variable=self.v_mari,bg=BG_DARK,fg=TEXT_SEC,
                       selectcolor=BG_INPUT,activebackground=BG_DARK,font=("Segoe UI",9),
                       command=self._search).pack(side="left",padx=8)
        self.v_baixo=tk.BooleanVar()
        tk.Checkbutton(fil,text="Estoque baixo < 5",variable=self.v_baixo,bg=BG_DARK,fg=ACCENT_RED,
                       selectcolor=BG_INPUT,activebackground=BG_DARK,font=("Segoe UI",9,"bold"),
                       command=self._search).pack(side="left")
        styled_btn(fil,"Filtrar",bg=ACCENT,cmd=self._search,w=8).pack(side="left",padx=8)
        styled_btn(fil,"↺",bg=BG_CARD,fg=TEXT_SEC,cmd=self._reload,w=3).pack(side="right")

        cols=("ID","Nome","Categoria","Preço","Estoque","Mari")
        frm,self.tv=build_treeview(self,cols); frm.pack(fill="both",expand=True,padx=28,pady=(0,8))
        for col,w,a in zip(cols,(50,200,100,90,80,60),("center","w","center","e","center","center")):
            self.tv.heading(col,text=col); self.tv.column(col,width=w,anchor=a)

        act=tk.Frame(self,bg=BG_PANEL); act.pack(fill="x",padx=28,pady=(4,20))
        styled_btn(act,"✏ Editar",bg=ACCENT,cmd=self._edit).pack(side="left",padx=(0,8))
        styled_btn(act,"🗑 Excluir",bg=ACCENT_RED,cmd=self._delete).pack(side="left",padx=(0,8))
        styled_btn(act,"📋 Relatório",bg=BG_CARD,fg=ACCENT_YEL,cmd=self._relatorio).pack(side="left")

    def _reload(self):
        self.sv.set(""); self.v_mari.set(False); self.v_baixo.set(False)
        self.e_pmin.delete(0,"end"); self.e_pmax.delete(0,"end")
        try: self._populate(ProdutoDAO.listar_todos())
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _search(self,*_):
        nome=self.sv.get().strip()
        pmin=float(self.e_pmin.get()) if self.e_pmin.get().strip() else None
        pmax=float(self.e_pmax.get()) if self.e_pmax.get().strip() else None
        mari=self.v_mari.get() or None; baixo=self.v_baixo.get()
        try: self._populate(ProdutoDAO.pesquisar(nome=nome,preco_min=pmin,preco_max=pmax,
                                                  fabricado_em_mari=mari,estoque_baixo=baixo))
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _populate(self, lst):
        self.tv.delete(*self.tv.get_children())
        for i,p in enumerate(lst):
            tag = "baixo" if p.quantidade < 5 else ("alt" if i%2 else "")
            self.tv.insert("","end",iid=str(p.id_produto),
                           values=(p.id_produto,p.nome,p.categoria,
                                   f"R$ {p.preco:.2f}",p.quantidade,"✓" if p.fabricado_em_mari else "—"),
                           tags=(tag,))
        n=len(lst); self.lbl_cnt.config(text=f"  {n} produto{'s'if n!=1 else''}")

    def _novo(self): ProdutoForm(self,self.root_win,on_save=lambda _:self._reload())
    def _sel(self):
        s=self.tv.selection()
        if not s: messagebox.showinfo("SmartClinic","Selecione um produto."); return None
        try: return ProdutoDAO.buscar_por_id(int(s[0]))
        except Exception as e: messagebox.showerror("Erro",str(e)); return None
    def _edit(self):
        p=self._sel()
        if p: ProdutoForm(self,self.root_win,produto=p,on_save=lambda _:self._reload())
    def _delete(self):
        p=self._sel()
        if not p: return
        if messagebox.askyesno("Confirmar",f"Excluir '{p.nome}'?",icon="warning"):
            try: ProdutoDAO.remover(p.id_produto); _toast(self.root_win,"✓ Produto removido.",ACCENT_RED); self._reload()
            except Exception as e: messagebox.showerror("Erro",str(e))
    def _relatorio(self):
        try: r=ProdutoDAO.gerar_relatorio()
        except Exception as e: messagebox.showerror("Erro",str(e)); return
        win=tk.Toplevel(self); win.title("Relatório de Estoque"); win.configure(bg=BG_PANEL)
        win.geometry("360x300"); win.resizable(False,False); win.grab_set()
        tk.Label(win,text="📦 Relatório de Estoque",bg=BG_PANEL,fg=TEXT_PRI,
                 font=("Segoe UI",14,"bold")).pack(pady=(20,10),padx=24,anchor="w")
        tk.Frame(win,bg=BORDER,height=1).pack(fill="x",padx=24)
        for lbl,val,cor in [("Total de produtos",r["total_produtos"],ACCENT),
                             ("Unidades em estoque",r["unidades_total"],ACCENT_GREEN),
                             ("Valor total do estoque",f"R$ {r['valor_estoque']:.2f}",ACCENT_YEL),
                             ("Preço médio",f"R$ {r['preco_medio']:.2f}",ACCENT),
                             ("Com estoque baixo (<5)",r["estoque_baixo"],ACCENT_RED)]:
            row=tk.Frame(win,bg=BG_PANEL); row.pack(fill="x",padx=28,pady=6)
            tk.Label(row,text=lbl,bg=BG_PANEL,fg=TEXT_SEC,font=("Segoe UI",10)).pack(side="left")
            tk.Label(row,text=str(val),bg=BG_PANEL,fg=cor,font=("Segoe UI",13,"bold")).pack(side="right")
        styled_btn(win,"Fechar",cmd=win.destroy).pack(pady=14)

class ProdutoForm(tk.Toplevel):
    def __init__(self, parent, root_win, on_save, produto=None):
        super().__init__(parent); self.root_win=root_win; self.on_save=on_save; self.produto=produto
        self.title("Novo Produto" if not produto else "Editar Produto")
        self.configure(bg=BG_PANEL); self.geometry("460x500"); self.resizable(False,False); self.grab_set()
        p=produto
        tk.Label(self,text="Novo Produto" if not p else "Editar Produto",
                 bg=BG_PANEL,fg=TEXT_PRI,font=("Segoe UI",15,"bold")).pack(pady=(20,6),padx=24,anchor="w")
        tk.Frame(self,bg=BORDER,height=1).pack(fill="x",padx=24,pady=(0,6))
        self.e_nome  =labeled_entry(self,"Nome *",          p.nome          if p else "")
        self.e_desc  =labeled_entry(self,"Descrição",       p.descricao or "" if p else "")
        self.e_preco =labeled_entry(self,"Preço (R$) *",    str(p.preco)    if p else "")
        self.e_qtd   =labeled_entry(self,"Quantidade *",    str(p.quantidade) if p else "0")
        self.e_cat   =labeled_entry(self,"Categoria",       p.categoria     if p else "Geral")
        self.v_mari  =labeled_check(self,"Fabricado em Mari",p.fabricado_em_mari if p else False)
        tk.Frame(self,bg=BORDER,height=1).pack(fill="x",padx=24,pady=(10,0))
        btns=tk.Frame(self,bg=BG_PANEL); btns.pack(fill="x",padx=24,pady=14)
        styled_btn(btns,"✕ Cancelar",bg=BG_CARD,fg=TEXT_SEC,cmd=self.destroy).pack(side="left")
        styled_btn(btns,"✔ Salvar",bg=ACCENT_GREEN,cmd=self._salvar).pack(side="right")

    def _salvar(self):
        nome=self.e_nome.get().strip(); desc=self.e_desc.get().strip() or None
        cat=self.e_cat.get().strip() or "Geral"; mari=self.v_mari.get()
        try:
            preco=float(self.e_preco.get()); qtd=int(self.e_qtd.get())
        except: messagebox.showwarning("Atenção","Preço e quantidade devem ser numéricos.",parent=self); return
        if not nome: messagebox.showwarning("Atenção","Nome obrigatório.",parent=self); return
        try:
            if not self.produto:
                nid=ProdutoDAO.inserir(nome,desc,preco,qtd,cat,mari)
                salvo=ProdutoDAO.buscar_por_id(nid); _toast(self.root_win,"✓ Produto cadastrado!")
            else:
                ProdutoDAO.alterar(self.produto.id_produto,nome,desc,preco,qtd,cat,mari)
                salvo=ProdutoDAO.buscar_por_id(self.produto.id_produto); _toast(self.root_win,"✓ Produto atualizado!")
            self.on_save(salvo); self.destroy()
        except Exception as e: messagebox.showerror("Erro",str(e),parent=self)

# ════════════════════════════════════════════════════════════════
#  PÁGINA — COMPRAS
# ════════════════════════════════════════════════════════════════
class ComprasPage(tk.Frame):
    def __init__(self, parent, root_win):
        super().__init__(parent, bg=BG_DARK); self.root_win=root_win; self._build(); self._reload()

    def _build(self):
        hdr=section_header(self,"Compras")
        self.lbl_cnt=tk.Label(hdr,text="",bg=BG_DARK,fg=TEXT_SEC,font=("Segoe UI",11)); self.lbl_cnt.pack(side="left",pady=4)
        styled_btn(hdr,"+ Nova Compra",cmd=self._nova).pack(side="right")

        cols=("ID","Cliente","Vendedor","Data","Pagamento","Status","Desconto","Total")
        frm,self.tv=build_treeview(self,cols); frm.pack(fill="both",expand=True,padx=28,pady=(16,8))
        for col,w,a in zip(cols,(50,150,120,140,90,90,70,100),
                           ("center","w","center","center","center","center","center","e")):
            self.tv.heading(col,text=col); self.tv.column(col,width=w,anchor=a)

        act=tk.Frame(self,bg=BG_PANEL); act.pack(fill="x",padx=28,pady=(4,8))
        styled_btn(act,"✓ Confirmar Pagamento",bg=ACCENT_GREEN,cmd=self._confirmar).pack(side="left",padx=(0,8))
        styled_btn(act,"🔍 Ver Itens",bg=BG_CARD,fg=ACCENT,cmd=self._ver_itens).pack(side="left",padx=(0,8))
        styled_btn(act,"📊 Relatório Mensal",bg=BG_CARD,fg=ACCENT_YEL,cmd=self._rel_mensal).pack(side="left")
        styled_btn(act,"↺ Atualizar",bg=BG_CARD,fg=TEXT_SEC,cmd=self._reload).pack(side="right")

        # cards de total
        self.totals_frame=tk.Frame(self,bg=BG_DARK); self.totals_frame.pack(fill="x",padx=28,pady=(0,16))
        self.tot_widgets={}
        for title,clr in [("Faturamento Total",ACCENT_GREEN),("Pendentes",ACCENT_YEL),("Total Compras",ACCENT)]:
            c=tk.Frame(self.totals_frame,bg=BG_CARD,padx=20,pady=10); c.pack(side="left",padx=(0,10))
            lbl=tk.Label(c,text="—",bg=BG_CARD,fg=clr,font=("Segoe UI",16,"bold")); lbl.pack()
            tk.Label(c,text=title,bg=BG_CARD,fg=TEXT_SEC,font=("Segoe UI",9)).pack()
            self.tot_widgets[title]=lbl

    def _reload(self):
        try:
            cs=CompraDAO.listar_todas(); self.tv.delete(*self.tv.get_children())
            for i,c in enumerate(cs):
                tag = "confirmado" if c.status_pagamento=="confirmado" else "pendente"
                self.tv.insert("","end",iid=str(c.id_compra),
                               values=(c.id_compra,c.nome_cliente,c.nome_vendedor,
                                       str(c.data_compra)[:16],c.forma_pagamento,
                                       c.status_pagamento,
                                       f"{c.desconto_pct:.0f}%" if c.desconto_pct else "—",
                                       f"R$ {c.valor_total:.2f}"),tags=(tag,))
            n=len(cs); self.lbl_cnt.config(text=f"  {n} compra{'s'if n!=1 else''}")
            r=CompraDAO.gerar_relatorio_geral()
            self.tot_widgets["Faturamento Total"].config(text=f"R$ {r['faturamento_total']:.2f}")
            self.tot_widgets["Pendentes"].config(text=str(r["pendentes"]))
            self.tot_widgets["Total Compras"].config(text=str(r["total_compras"]))
        except Exception as e: messagebox.showerror("Erro",str(e))

    def _sel_id(self):
        s=self.tv.selection()
        if not s: messagebox.showinfo("SmartClinic","Selecione uma compra."); return None
        return int(s[0])

    def _confirmar(self):
        cid=self._sel_id()
        if cid is None: return
        if messagebox.askyesno("Confirmar","Confirmar pagamento desta compra?"):
            try: CompraDAO.confirmar_pagamento(cid); _toast(self.root_win,"✓ Pagamento confirmado!"); self._reload()
            except Exception as e: messagebox.showerror("Erro",str(e))

    def _ver_itens(self):
        cid=self._sel_id()
        if cid is None: return
        try: itens=CompraDAO.buscar_itens(cid)
        except Exception as e: messagebox.showerror("Erro",str(e)); return
        win=tk.Toplevel(self); win.title(f"Itens — Compra #{cid}"); win.configure(bg=BG_PANEL)
        win.geometry("500x340"); win.resizable(False,False); win.grab_set()
        tk.Label(win,text=f"🧾  Itens da Compra #{cid}",bg=BG_PANEL,fg=TEXT_PRI,
                 font=("Segoe UI",13,"bold")).pack(pady=(20,8),padx=24,anchor="w")
        tk.Frame(win,bg=BORDER,height=1).pack(fill="x",padx=24)
        cols2=("Produto","Qtd","Preço Unit.","Subtotal")
        frm2,tv2=build_treeview(win,cols2); frm2.pack(fill="both",expand=True,padx=16,pady=12)
        for col,w in zip(cols2,(220,60,100,100)):
            tv2.heading(col,text=col); tv2.column(col,width=w,anchor="center")
        total=0.0
        for i,it in enumerate(itens):
            tv2.insert("","end",values=(it.nome_produto,it.quantidade,
                       f"R$ {it.preco_unitario:.2f}",f"R$ {it.subtotal:.2f}"),
                       tags=("alt",) if i%2 else ()); total+=it.subtotal
        tk.Label(win,text=f"Total bruto: R$ {total:.2f}",bg=BG_PANEL,fg=TEXT_SEC,
                 font=("Segoe UI",9)).pack(padx=24,anchor="e")
        styled_btn(win,"Fechar",cmd=win.destroy).pack(pady=10)

    def _nova(self): NovaCompraForm(self,self.root_win,on_save=lambda _:self._reload())

    def _rel_mensal(self):
        hoje=datetime.date.today()
        try: dados=CompraDAO.relatorio_mensal(hoje.year,hoje.month)
        except Exception as e: messagebox.showerror("Erro",str(e)); return
        win=tk.Toplevel(self); win.title("Relatório Mensal"); win.configure(bg=BG_PANEL)
        win.geometry("520x380"); win.resizable(False,False); win.grab_set()
        mes=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"][hoje.month-1]
        tk.Label(win,text=f"📊  Vendas por Vendedor — {mes}/{hoje.year}",bg=BG_PANEL,fg=TEXT_PRI,
                 font=("Segoe UI",13,"bold")).pack(pady=(20,8),padx=24,anchor="w")
        tk.Frame(win,bg=BORDER,height=1).pack(fill="x",padx=24)
        cols=("Vendedor","Nº Vendas","Faturamento","Ticket Médio")
        frm,tv=build_treeview(win,cols); frm.pack(fill="both",expand=True,padx=16,pady=12)
        for col,w in zip(cols,(200,80,120,120)):
            tv.heading(col,text=col); tv.column(col,width=w,anchor="center")
        if not dados:
            tv.insert("","end",values=("Sem compras confirmadas neste mês","—","—","—"))
        else:
            for i,d in enumerate(dados):
                tv.insert("","end",values=(d["vendedor"],d["total_vendas"],
                          f"R$ {d['faturamento']:.2f}",f"R$ {d['ticket_medio']:.2f}"),
                          tags=("alt",) if i%2 else ())
        styled_btn(win,"Fechar",cmd=win.destroy).pack(pady=12)

class NovaCompraForm(tk.Toplevel):
    """Formulário para realizar uma nova compra com múltiplos itens."""
    def __init__(self, parent, root_win, on_save):
        super().__init__(parent); self.root_win=root_win; self.on_save=on_save
        self.title("Nova Compra"); self.configure(bg=BG_PANEL)
        self.geometry("580x780"); self.resizable(False, True); self.grab_set()
        self.minsize(580, 600)
        self.itens_carrinho = []  # [{"id_produto":x,"quantidade":y,"nome":z,"preco":w}]
        self._build()

    def _build(self):
        # ── Canvas com scroll vertical para garantir que os botões fiquem visíveis ──
        canvas = tk.Canvas(self, bg=BG_PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_PANEL)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(inner_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", _on_frame_configure)

        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Conteúdo do formulário ──
        tk.Label(inner, text="Nova Compra", bg=BG_PANEL, fg=TEXT_PRI,
                 font=("Segoe UI", 15, "bold")).pack(pady=(18, 4), padx=24, anchor="w")
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 6))

        # Cliente
        try: clientes = ClienteDAO.listar_todos()
        except: clientes = []
        self.cli_opts = {f"{c.id_cliente} — {c.nome}": c for c in clientes}
        _, self.v_cli = labeled_combo(inner, "Cliente *", list(self.cli_opts.keys()))

        # Vendedor
        try: vendedores = VendedorDAO.listar_todos()
        except: vendedores = []
        self.vnd_opts = {f"{v.id_vendedor} — {v.nome}": v for v in vendedores}
        _, self.v_vnd = labeled_combo(inner, "Vendedor *", list(self.vnd_opts.keys()))

        # Forma pagamento
        _, self.v_pag = labeled_combo(inner, "Forma de Pagamento *",
                                      ["dinheiro", "cartao", "boleto", "pix", "berries"])

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=24, pady=8)
        tk.Label(inner, text="Adicionar Produto ao Carrinho", bg=BG_PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 10, "bold")).pack(padx=24, anchor="w")

        try: produtos = ProdutoDAO.listar_todos()
        except: produtos = []
        self.prod_opts = {f"{p.id_produto} — {p.nome} (R${p.preco:.2f} | estq:{p.quantidade})": p for p in produtos}
        _, self.v_prod = labeled_combo(inner, "Produto", list(self.prod_opts.keys()))
        self.e_qtd = labeled_entry(inner, "Quantidade", "1")

        styled_btn(inner, "＋ Adicionar ao Carrinho", bg=ACCENT,
                   cmd=self._add_item).pack(padx=24, pady=6, anchor="e")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=24)
        tk.Label(inner, text="Carrinho", bg=BG_PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 10, "bold")).pack(padx=24, anchor="w", pady=(6, 0))

        cols = ("Produto", "Qtd", "Preço Un.", "Subtotal")
        frm, self.tv_cart = build_treeview(inner, cols)
        frm.pack(fill="x", padx=24, pady=(4, 0))
        for col, w in zip(cols, (220, 50, 90, 90)):
            self.tv_cart.heading(col, text=col)
            self.tv_cart.column(col, width=w, anchor="center")
        self.tv_cart.config(height=4)

        bot = tk.Frame(inner, bg=BG_PANEL); bot.pack(fill="x", padx=24, pady=4)
        styled_btn(bot, "🗑 Remover Item", bg=ACCENT_RED,
                   cmd=self._rem_item, w=16).pack(side="left")
        self.lbl_total = tk.Label(bot, text="Total: R$ 0,00", bg=BG_PANEL, fg=ACCENT_GREEN,
                                  font=("Segoe UI", 11, "bold"))
        self.lbl_total.pack(side="right")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=24, pady=8)
        btns = tk.Frame(inner, bg=BG_PANEL); btns.pack(fill="x", padx=24, pady=(4, 24))
        styled_btn(btns, "✕ Cancelar", bg=BG_CARD, fg=TEXT_SEC,
                   cmd=self.destroy).pack(side="left")
        styled_btn(btns, "✔ Finalizar Compra", bg=ACCENT_GREEN,
                   cmd=self._finalizar).pack(side="right")

    def _add_item(self):
        key=self.v_prod.get()
        if not key or key not in self.prod_opts:
            messagebox.showwarning("Atenção","Selecione um produto.",parent=self); return
        try: qtd=int(self.e_qtd.get())
        except: messagebox.showwarning("Atenção","Quantidade inválida.",parent=self); return
        p=self.prod_opts[key]
        self.itens_carrinho.append({"id_produto":p.id_produto,"quantidade":qtd,"nome":p.nome,"preco":p.preco})
        self._atualizar_cart()

    def _rem_item(self):
        s=self.tv_cart.selection()
        if not s: return
        idx=int(s[0]); del self.itens_carrinho[idx]; self._atualizar_cart()

    def _atualizar_cart(self):
        self.tv_cart.delete(*self.tv_cart.get_children())
        total=0.0
        for i,it in enumerate(self.itens_carrinho):
            sub=it["preco"]*it["quantidade"]; total+=sub
            self.tv_cart.insert("","end",iid=str(i),
                                values=(it["nome"],it["quantidade"],f"R$ {it['preco']:.2f}",f"R$ {sub:.2f}"),
                                tags=("alt",) if i%2 else ())
        self.lbl_total.config(text=f"Total: R$ {total:.2f}")

    def _finalizar(self):
        cli_key=self.v_cli.get(); vnd_key=self.v_vnd.get(); pag=self.v_pag.get()
        if not cli_key or cli_key not in self.cli_opts:
            messagebox.showwarning("Atenção","Selecione um cliente.",parent=self); return
        if not vnd_key or vnd_key not in self.vnd_opts:
            messagebox.showwarning("Atenção","Selecione um vendedor.",parent=self); return
        if not pag:
            messagebox.showwarning("Atenção","Selecione a forma de pagamento.",parent=self); return
        if not self.itens_carrinho:
            messagebox.showwarning("Atenção","Adicione pelo menos um produto.",parent=self); return
        cli=self.cli_opts[cli_key]; vnd=self.vnd_opts[vnd_key]
        desc_txt=" (10% de desconto aplicado! 🎉)" if cli.tem_desconto else ""
        if not messagebox.askyesno("Confirmar",f"Finalizar compra para {cli.nome}?{desc_txt}",parent=self): return
        itens=[{"id_produto":it["id_produto"],"quantidade":it["quantidade"]} for it in self.itens_carrinho]
        try:
            nid=CompraDAO.realizar(cli.id_cliente,vnd.id_vendedor,pag,itens)
            _toast(self.root_win,f"✓ Compra #{nid} registrada!"); self.on_save(nid); self.destroy()
        except Exception as e: messagebox.showerror("Erro na Compra",str(e),parent=self)

# ════════════════════════════════════════════════════════════════
#  TELA DE ERRO DE CONEXÃO
# ════════════════════════════════════════════════════════════════
class ConexaoErroPage(tk.Frame):
    def __init__(self, parent, msg):
        super().__init__(parent,bg=BG_DARK)
        tk.Label(self,text="⚠",bg=BG_DARK,fg=ACCENT_RED,font=("Segoe UI",48)).pack(pady=(60,8))
        tk.Label(self,text="Não foi possível conectar ao banco de dados",bg=BG_DARK,
                 fg=TEXT_PRI,font=("Segoe UI",15,"bold")).pack()
        tk.Label(self,text=msg,bg=BG_DARK,fg=TEXT_SEC,font=("Segoe UI",10),wraplength=520).pack(pady=12)
        tk.Label(self,text="Verifique se o MySQL está rodando e se o arquivo secreto.env existe\n"
                 "com: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME",
                 bg=BG_DARK,fg=TEXT_MUT,font=("Segoe UI",9),wraplength=520).pack()

# ════════════════════════════════════════════════════════════════
#  APLICAÇÃO PRINCIPAL
# ════════════════════════════════════════════════════════════════
class SmartClinic:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("SmartClinic — Sistema Integrado de Gestão Clínica")
        self.root.configure(bg=BG_DARK); self.root.geometry("1180x720"); self.root.minsize(1000,620)
        self._build(); self.root.mainloop()

    def _build(self):
        self.sidebar=tk.Frame(self.root,bg=BG_PANEL,width=SIDEBAR_W)
        self.sidebar.pack(side="left",fill="y"); self.sidebar.pack_propagate(False)

        lf=tk.Frame(self.sidebar,bg=BG_PANEL,pady=20); lf.pack(fill="x")
        tk.Label(lf,text="⚕",bg=BG_PANEL,fg=ACCENT,font=("Segoe UI",24)).pack()
        tk.Label(lf,text="SmartClinic",bg=BG_PANEL,fg=TEXT_PRI,font=("Segoe UI",13,"bold")).pack()
        tk.Label(lf,text="Gestão Clínica v2.0",bg=BG_PANEL,fg=TEXT_MUT,font=("Segoe UI",8)).pack()
        clr=ACCENT_GREEN if DB_DISPONIVEL else ACCENT_RED
        tk.Label(lf,text="● MySQL Conectado" if DB_DISPONIVEL else "● Sem Conexão",
                 bg=BG_PANEL,fg=clr,font=("Segoe UI",8)).pack(pady=(4,0))
        tk.Frame(self.sidebar,bg=BORDER,height=1).pack(fill="x",padx=16,pady=6)

        self.nav_items={}; self.active_page=None
        menu=([ ("📊","Dashboard",  lambda p:DashboardPage(p,self.root)),
                ("👥","Clientes",   lambda p:ClientesPage(p,self.root)),
                ("👨‍⚕️","Vendedores", lambda p:VendedoresPage(p,self.root)),
                ("📦","Produtos",   lambda p:ProdutosPage(p,self.root)),
                ("💳","Compras",    lambda p:ComprasPage(p,self.root)),
               ] if DB_DISPONIVEL else
               [("⚠","Conexão",    lambda p:ConexaoErroPage(p,_DB_ERRO_MSG))])

        for icon,label,_ in menu: self._nav_item(icon,label)
        tk.Frame(self.sidebar,bg=BORDER,height=1).pack(fill="x",padx=16,pady=10)
        tk.Label(self.sidebar,text="SmartClinic © 2026",bg=BG_PANEL,fg=TEXT_MUT,font=("Segoe UI",7)).pack(side="bottom",pady=10)

        self.main_area=tk.Frame(self.root,bg=BG_DARK); self.main_area.pack(side="left",fill="both",expand=True)
        topbar=tk.Frame(self.main_area,bg=BG_PANEL,height=48); topbar.pack(fill="x"); topbar.pack_propagate(False)
        self.topbar_title=tk.Label(topbar,text="",bg=BG_PANEL,fg=TEXT_PRI,font=("Segoe UI",11,"bold"))
        self.topbar_title.pack(side="left",padx=20,pady=12)
        tk.Label(topbar,text="Admin  ▾",bg=BG_PANEL,fg=TEXT_SEC,font=("Segoe UI",10)).pack(side="right",padx=20)
        tk.Label(topbar,text="🔔",bg=BG_PANEL,fg=TEXT_SEC,font=("Segoe UI",12)).pack(side="right")

        self.content=tk.Frame(self.main_area,bg=BG_DARK); self.content.pack(fill="both",expand=True)
        self.pages={}
        for _,label,factory in menu:
            page=factory(self.content); page.place(relx=0,rely=0,relwidth=1,relheight=1); self.pages[label]=page
        self._switch(list(self.pages.keys())[0])

    def _nav_item(self,icon,label):
        bf=tk.Frame(self.sidebar,bg=BG_PANEL,cursor="hand2"); bf.pack(fill="x",padx=10,pady=2)
        bar=tk.Frame(bf,bg=BG_PANEL,width=3); bar.pack(side="left",fill="y")
        inn=tk.Frame(bf,bg=BG_PANEL,padx=10,pady=10); inn.pack(fill="x",side="left")
        il=tk.Label(inn,text=icon,bg=BG_PANEL,fg=TEXT_SEC,font=("Segoe UI",13)); il.pack(side="left")
        ll=tk.Label(inn,text=label,bg=BG_PANEL,fg=TEXT_SEC,font=("Segoe UI",10)); ll.pack(side="left",padx=10)
        ws=(bf,inn,il,ll,bar)
        def on_e(e,ww=ws):
            if self.active_page!=label:
                for w in ww: w.config(bg="#1C2236")
        def on_l(e,ww=ws):
            if self.active_page!=label:
                for w in ww: w.config(bg=BG_PANEL)
        for w in ws:
            w.bind("<Button-1>",lambda e,l=label:self._switch(l))
            w.bind("<Enter>",on_e); w.bind("<Leave>",on_l)
        self.nav_items[label]=(ws,bar)

    def _switch(self,name):
        if self.active_page and self.active_page in self.nav_items:
            pw,pb=self.nav_items[self.active_page]
            for w in pw: w.config(bg=BG_PANEL)
            pb.config(bg=BG_PANEL); pw[2].config(fg=TEXT_SEC); pw[3].config(fg=TEXT_SEC)
        self.active_page=name; ws,bar=self.nav_items[name]
        for w in ws: w.config(bg="#1C2A45")
        bar.config(bg=ACCENT,width=3); ws[2].config(fg=ACCENT); ws[3].config(fg=TEXT_PRI)
        self.pages[name].lift(); self.topbar_title.config(text=name)

if __name__ == "__main__":
    SmartClinic()