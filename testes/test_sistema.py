import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sistema.biblioteca import Biblioteca


class TestBiblioteca(unittest.TestCase):
    """Testes resilientes a refatorações, validando comportamento público."""

    def setUp(self):
        """Toda execução começa com uma biblioteca vazia e arquivo limpo."""
        self.arquivo = "test_biblioteca.json"

        if os.path.exists(self.arquivo):
            os.remove(self.arquivo)

        self.bib = Biblioteca(self.arquivo)

    def tearDown(self):
        """Limpa o arquivo após cada teste."""
        if os.path.exists(self.arquivo):
            os.remove(self.arquivo)

    # ------------------------------
    # TESTES DE COMPORTAMENTO (POO)
    # ------------------------------

    def test_adicionar_livro_valido(self):
        ok = self.bib.adicionar_livro("Livro Teste", "Autor", "1234567890123", 2024)
        self.assertTrue(ok)

        livros = self.bib.livros
        self.assertEqual(len(livros), 1)

        livro = livros[0]
        self.assertEqual(livro.titulo, "Livro Teste")
        self.assertEqual(livro.autor, "Autor")
        self.assertTrue(livro.disponivel)

    def test_cadastrar_usuario_valido(self):
        ok = self.bib.cadastrar_usuario("Usuário", "user@example.com", "9999")
        self.assertTrue(ok)

        usuarios = self.bib.usuarios
        self.assertEqual(len(usuarios), 1)
        self.assertEqual(usuarios[0].email, "user@example.com")

    def test_realizar_emprestimo_valido(self):
        self.bib.adicionar_livro("Livro A", "Autor A", "1234567890123", 2024)
        self.bib.cadastrar_usuario("Usuário A", "user@example.com", "123")

        ok = self.bib.realizar_emprestimo(1, 1)
        self.assertTrue(ok)

        livro = self.bib.livros[0]
        self.assertFalse(livro.disponivel)

        emprestimos = self.bib.emprestimos
        self.assertEqual(len(emprestimos), 1)
        self.assertEqual(emprestimos[0].usuario_id, 1)
        self.assertEqual(emprestimos[0].livro_id, 1)

    def test_devolver_livro_valido(self):
        self.bib.adicionar_livro("Livro A", "Autor A", "1234567890123", 2024)
        self.bib.cadastrar_usuario("Usuário A", "user@example.com", "123")
        self.bib.realizar_emprestimo(1, 1)

        ok = self.bib.devolver_livro(1)
        self.assertTrue(ok)

        livro = self.bib.livros[0]
        self.assertTrue(livro.disponivel)

        emp = self.bib.emprestimos[0]
        self.assertTrue(emp.devolvido)

    def test_salvar_e_carregar_dados(self):
        """Testa persistência de forma genérica e sólida."""
        self.bib.adicionar_livro("Livro X", "Autor X", "1234567890123", 2024)
        self.bib.cadastrar_usuario("Usuário X", "user@example.com", "123")
        self.bib.salvar_dados()

        nova = Biblioteca(self.arquivo)
        nova.carregar_dados()

        self.assertEqual(len(nova.livros), 1)
        self.assertEqual(len(nova.usuarios), 1)

        self.assertEqual(nova.livros[0].titulo, "Livro X")
        self.assertEqual(nova.usuarios[0].email, "user@example.com")

    # ------------------------------
    # TESTES DE ERROS
    # ------------------------------

    def test_nao_adicionar_livro_com_isbn_invalido(self):
        ok = self.bib.adicionar_livro("Livro B", "Autor B", "123", 2024)
        self.assertFalse(ok)
        self.assertEqual(len(self.bib.livros), 0) 

    def test_nao_adicionar_livro_com_isbn_duplicado(self):
        ok1 = self.bib.adicionar_livro("Livro A", "Autor A", "1234567890123", 2024)
        self.assertTrue(ok1)

        ok2 = self.bib.adicionar_livro("Livro B", "Autor B", "1234567890123", 2024)
        self.assertFalse(ok2)

        self.assertEqual(len(self.bib.livros), 1)
        self.assertEqual(self.bib.livros[0].titulo, "Livro A")

    def test_nao_cadastrar_usuario_com_email_invalido(self):
        ok = self.bib.cadastrar_usuario("Usuário", "emailinvalido", "999")
        self.assertFalse(ok)
        self.assertEqual(len(self.bib.usuarios), 0) 

    def test_nao_cadastrar_usuario_com_email_duplicado(self):
        ok1 = self.bib.cadastrar_usuario("Usuário A", "user@example.com", "111")
        self.assertTrue(ok1)

        ok2 = self.bib.cadastrar_usuario("Usuário B", "user@example.com", "222")
        self.assertFalse(ok2)

        self.assertEqual(len(self.bib.usuarios), 1)
        self.assertEqual(self.bib.usuarios[0].email, "user@example.com")

    def test_nao_permitir_emprestimo_para_usuario_inexistente(self):
        self.bib.adicionar_livro("Livro A", "Autor A", "1234567890123", 2024)
        ok = self.bib.realizar_emprestimo(99, 1)
        self.assertFalse(ok)

    def test_nao_permitir_emprestimo_para_livro_inexistente(self):
        self.bib.cadastrar_usuario("Usuário A", "user@example.com", "999")
        ok = self.bib.realizar_emprestimo(1, 99)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
