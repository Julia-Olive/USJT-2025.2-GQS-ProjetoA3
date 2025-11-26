import json
from sistema.livro import Livro
from sistema.usuario import Usuario
from sistema.emprestimo import Emprestimo
from sistema.fabrica import FabricaObjetos


class Biblioteca:
    def __init__(self, arquivo_dados='biblioteca.json'):
        # Listas que armazenam os objetos da aplicação
        self.livros = []          # Armazena todos os livros cadastrados
        self.usuarios = []        # Armazena todos os usuários cadastrados
        self.emprestimos = []     # Armazena todos os empréstimos realizados

        # Nome do arquivo onde os dados serão salvos/carregados
        self.arquivo = arquivo_dados

        # Contadores automáticos para gerar IDs únicos
        self.contador_livros = 1
        self.contador_usuarios = 1

    # ---------------------------------------------------------------------
    # -------------------------- MÉTODOS DE LIVRO -------------------------
    # ---------------------------------------------------------------------
    def adicionar_livro(self, titulo, autor, isbn, ano):
        """Adiciona um novo livro ao sistema, após validações."""

        # Verifica se os campos essenciais foram preenchidos
        if not titulo or not autor or not isbn:
            print("Erro: campos obrigatórios")
            return False

        # Valida tamanho do ISBN (10 ou 13 dígitos)
        if len(isbn) not in (10, 13):
            print("ISBN inválido")
            return False

        # Impede cadastro de livros duplicados pelo ISBN
        if any(livro.isbn == isbn for livro in self.livros):
            print("Livro já existe")
            return False

        # Cria o livro via fábrica de objetos (implementação separada)
        novo_livro = FabricaObjetos.criar_livro(
            self.contador_livros, titulo, autor, isbn, ano
        )

        # Adiciona à lista e incrementa o contador
        self.livros.append(novo_livro)
        self.contador_livros += 1

        print("Livro adicionado com sucesso.")
        self.salvar_dados()  # Atualiza o arquivo JSON
        return True

    # ---------------------------------------------------------------------
    # ------------------------- MÉTODOS DE USUÁRIO -------------------------
    # ---------------------------------------------------------------------
    def cadastrar_usuario(self, nome, email, telefone):
        """Cadastra um novo usuário após validações."""

        # Valida se nome existe e se o email contém "@"
        if not nome or "@" not in email:
            print("Nome ou email inválido")
            return False

        # Verifica se o email já foi cadastrado
        if any(u.email == email for u in self.usuarios):
            print("Email já cadastrado")
            return False

        # Cria o usuário via fábrica
        novo_usuario = FabricaObjetos.criar_usuario(
            self.contador_usuarios, nome, email, telefone
        )

        self.usuarios.append(novo_usuario)
        self.contador_usuarios += 1

        print("Usuário cadastrado com sucesso.")
        self.salvar_dados()
        return True

    # ---------------------------------------------------------------------
    # ----------------------- MÉTODOS DE EMPRÉSTIMO ------------------------
    # ---------------------------------------------------------------------
    def realizar_emprestimo(self, usuario_id, livro_id):
        """Realiza um empréstimo de um livro para um usuário."""

        # Busca usuário pelo ID
        usuario = next((u for u in self.usuarios if u.id == usuario_id), None)
        # Busca livro pelo ID
        livro = next((l for l in self.livros if l.id == livro_id), None)

        # Verificações básicas
        if not usuario:
            print("Usuário não encontrado.")
            return False

        if not livro:
            print("Livro não encontrado.")
            return False

        if not livro.disponivel:
            print("Livro não disponível.")
            return False

        # Cria o empréstimo
        emprestimo = FabricaObjetos.criar_emprestimo(
            len(self.emprestimos) + 1, usuario_id, livro_id
        )

        # Marca livro como indisponível
        livro.disponivel = False

        # Salva o empréstimo
        self.emprestimos.append(emprestimo)

        print("Empréstimo realizado com sucesso.")
        self.salvar_dados()
        return True

    def devolver_livro(self, emprestimo_id):
        """Devolve um livro e atualiza o status do empréstimo."""

        # Localiza o empréstimo por ID
        emprestimo = next((e for e in self.emprestimos if e.id == emprestimo_id), None)

        if not emprestimo:
            print("Empréstimo não encontrado.")
            return False

        if emprestimo.devolvido:
            print("Livro já devolvido.")
            return False

        # Encontra o livro vinculado ao empréstimo
        livro = next((l for l in self.livros if l.id == emprestimo.livro_id), None)
        if livro:
            livro.disponivel = True  # Torna o livro disponível novamente

        # Marca o empréstimo como devolvido
        emprestimo.devolver()

        print("Livro devolvido com sucesso.")
        self.salvar_dados()
        return True

    # ---------------------------------------------------------------------
    # --------------------------- MÉTODOS DE LISTAGEM ----------------------
    # ---------------------------------------------------------------------
    def listar_livros(self):
        """Exibe todos os livros cadastrados."""
        print("\n=== LIVROS ===")
        for livro in self.livros:
            print(livro)

    def listar_usuarios(self):
        """Exibe todos os usuários cadastrados."""
        print("\n=== USUÁRIOS ===")
        for usuario in self.usuarios:
            print(usuario)

    def listar_emprestimos(self):
        """Exibe todos os empréstimos realizados."""
        print("\n=== EMPRÉSTIMOS ===")
        for emp in self.emprestimos:
            print(emp)

    # ---------------------------------------------------------------------
    # ------------------------- PERSISTÊNCIA EM JSON -----------------------
    # ---------------------------------------------------------------------
    def salvar_dados(self):
        """Salva todos os dados da aplicação em um arquivo JSON."""

        dados = {
            'livros': [vars(l) for l in self.livros],                # Converte objetos em dicionários
            'usuarios': [vars(u) for u in self.usuarios],
            'emprestimos': [vars(e) for e in self.emprestimos],
            'contador_livros': self.contador_livros,
            'contador_usuarios': self.contador_usuarios
        }

        # Grava o arquivo JSON formatado
        with open(self.arquivo, 'w') as f:
            json.dump(dados, f, indent=2)

    def carregar_dados(self):
        """Carrega dados do arquivo JSON caso exista."""

        try:
            with open(self.arquivo, 'r') as f:
                dados = json.load(f)

                # Reconstrói os objetos a partir dos dicionários
                self.livros = [Livro(**l) for l in dados['livros']]
                self.usuarios = [Usuario(**u) for u in dados['usuarios']]
                self.emprestimos = [Emprestimo(**e) for e in dados['emprestimos']]

                # Recupera os contadores
                self.contador_livros = dados['contador_livros']
                self.contador_usuarios = dados['contador_usuarios']

            print("Dados carregados com sucesso.")

        except FileNotFoundError:
            # Caso o arquivo não exista, inicia com base limpa
            print("Arquivo de dados não encontrado, iniciando novo.")
