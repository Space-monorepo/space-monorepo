describe('Login Form', () => {
  beforeEach(() => {
    // Visita a página de login antes de cada teste
    // A baseUrl 'http://localhost:3000' é prefixada automaticamente
    cy.visit('/login');
  });

  it('should allow a user to log in with valid credentials', () => {
    // TODO: Ajuste os dados de login para credenciais válidas REAIS
    const userEmail = 'space@space.com'; // MUDE PARA UM EMAIL VÁLIDO DE TESTE
    const userPassword = 'spacepassword123'; // MUDE PARA UMA SENHA VÁLIDA DE TESTE

    // Encontra o campo de email pelo atributo name, digita o email e verifica o valor
    cy.get('[name="email"]') 
      .type(userEmail)
      .should('have.value', userEmail);

    // Encontra o campo de senha pelo atributo name, digita a senha e verifica o valor
    cy.get('[name="password"]') 
      .type(userPassword)
      .should('have.value', userPassword);

    // Encontra o botão de submit e clica nele
    cy.get('button[type="submit"]') 
      .click();

    // TODO: Adicione asserções para verificar se o login foi bem-sucedido
    // Exemplo: verificar se foi redirecionado para a página correta
    // cy.url().should('include', '/home'); 
    // Exemplo: verificar se um elemento específico da página de dashboard está visível
    // cy.get('.dashboard-header').should('be.visible');
  });

  it('should display an error message with invalid credentials', () => {
    // TODO: Ajuste os dados de login para credenciais inválidas REAIS
    const invalidEmail = 'usuario_invalido@exemplo.com';
    const invalidPassword = 'senha_invalida_123';

    cy.get('[name="email"]').type(invalidEmail);
    cy.get('[name="password"]').type(invalidPassword);
    cy.get('button[type="submit"]').click();

    // TODO: Adicione asserções para verificar se a mensagem de erro é exibida
    // Exemplo: 
    // cy.get('.error-message') // Substitua pelo seletor da sua mensagem de erro
    //   .should('be.visible')
    //   .and('contain', 'Credenciais inválidas'); 
  });

  // Você pode adicionar mais testes aqui, como:
  // - Testar campos obrigatórios
  // - Testar links como "Esqueci minha senha"
  // - Etc.
});
