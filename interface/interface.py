from tkinter import *

root = Tk()

class Application():
    def __init__(self):
        self.root = root
        self.tela()
        self.frames_da_tela()
        self.windgtes_frame1()
        root.mainloop()
    def tela(self):
        self.root.title("SmartClinic - Integrated Clinic Management and Sales System")
        self.root.configure(background="#2A1313")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        self.root.maxsize(width=900, height=700)
        self.root.minsize(width=500, height=400)
    def frames_da_tela(self):
        self.frame_1 = Frame(self.root, bd = 4, bg="#FFFFFF", highlightbackground="#F9F9F9", highlightthickness=3)
        
        self.frame_1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.46)

        self.frame_2 = Frame(self.root, bd = 4, bg="#FFFFFF", highlightbackground="#FFFFFF", highlightthickness=3)
        
        self.frame_2.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.46)
    def windgtes_frame1(self):
        #Criação do botao para limpar
        self.bt_limpar = Button(self.frame_1, text="Limpar")
        self.bt_limpar.place(relx=0.01, rely=0.01, relwidth=0.1, relheight=0.15)
        #Criação do botao para buscar
        self.bt_limpar = Button(self.frame_1, text="Buscar")
        self.bt_limpar.place(relx=0.12, rely=0.01, relwidth=0.1, relheight=0.15)
        #Criação do botão novo
        self.bt_novo = Button(self.frame_1, text="Novo")
        self.bt_novo.place(relx=0.6, rely=0.01, relwidth=0.1, relheight=0.15)
        #Criação do botão alterar
        self.bt_alterar = Button(self.frame_1, text="Alterar")
        self.bt_alterar.place(relx=0.7, rely=0.01, relwidth=0.1, relheight=0.15)
        #Criação do botão excluir
        self.bt_excluir = Button(self.frame_1, text="Excluir")
        self.bt_excluir.place(relx=0.8, rely=0.01, relwidth=0.1, relheight=0.15)
        #Criação do label e entrada do codigo
        self.lb_codigo = Label(self.frame_1, text="Código",)
        self.lb_codigo.place(relx=0.05, rely=0.35)

        self.codigo_entry = Entry(self.frame_1)
        self.codigo_entry.place(relx=0.05, rely=0.45, relwidth=0.8,)
        
        #Criação do label e entrada do nome
        self.lb_nome = Label(self.frame_1, text="Nome",)
        self.lb_nome.place(relx=0.05, rely=0.6)

        self.nome_entry = Entry(self.frame_1)
        self.nome_entry.place(relx=0.05, rely=0.7, relwidth=0.8,)

        #Criação do label e entrada do Telefone
        self.lb_telefone = Label(self.frame_1, text="Telefone",)
        self.lb_telefone.place(relx=0.05, rely=0.6)

        self.telefone_entry = Entry(self.frame_1)
        self.telefone_entry.place(relx=0.05, rely=0.7, relwidth=0.4,)

        #Criação do label e entrada do Email
        self.lb_email = Label(self.frame_1, text="Email",)
        self.lb_email.place(relx=0.5, rely=0.6)

        self.email_entry = Entry(self.frame_1)
        self.email_entry.place(relx=0.5, rely=0.7, relwidth=0.4,)



Application()