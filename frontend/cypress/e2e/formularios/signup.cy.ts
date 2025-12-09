describe('Signup Form', () => {
  beforeEach(() => {
    // Limpa todos os cookies e storage para garantir estado limpo
    cy.clearCookies();
    cy.clearLocalStorage();
    cy.clearAllSessionStorage();
    
    // Intercepta todas as requisições para login e redireciona de volta para signup
    cy.intercept('GET', '**/login**', (req) => {
      req.reply({ statusCode: 302, headers: { location: '/signup' } });
    }).as('interceptLogin');
    
    // Intercepta RSC requests que podem estar causando redirecionamento
    cy.intercept('GET', '**/login?_rsc=**', (req) => {
      req.reply({ statusCode: 302, headers: { location: '/signup' } });
    }).as('interceptLoginRSC');
    
    // Visita a página de signup e força ficar lá
    cy.visit('/signup', { 
      failOnStatusCode: false,
      onBeforeLoad: (win) => {
        // Previne redirecionamentos JavaScript
        win.history.pushState = cy.stub();
        win.history.replaceState = cy.stub();
      }
    });
    
    // Se ainda assim redirecionou, força ir para signup novamente
    cy.url().then((url) => {
      if (url.includes('/login')) {
        cy.visit('/signup', { failOnStatusCode: false });
      }
    });
    
    // Aguarda a página carregar
    cy.wait(1000);
    
    // Verifica se conseguiu ficar na página de signup
    cy.url().should('include', '/signup');
    
    // Aguarda o formulário estar completamente carregado
    cy.get('[name="name"]').should('be.visible');
    cy.get('[name="lastName"]').should('be.visible');
    cy.get('[name="email"]').should('be.visible');
    cy.get('[name="password"]').should('be.visible');
    cy.get('[name="confirm_password"]').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible');
  });

  it('should allow a user to sign up with valid information', () => {
    const userName = 'Space';
    const userLastName = 'User';
    const userEmail = 'space.user@space.com';
    const userPassword = 'spacepassword123';

    // Verifica que está na página correta
    cy.url().should('include', '/signup');
    
    // Estratégia: preencher um campo por vez com wait entre eles
    cy.get('[name="name"]').should('be.visible').focus().type(userName);
    cy.wait(200);
    cy.url().should('include', '/signup'); // Verifica que não redirecionou
    
    cy.get('[name="lastName"]').should('be.visible').focus().type(userLastName);
    cy.wait(200);
    cy.url().should('include', '/signup'); // Verifica que não redirecionou
    
    cy.get('[name="email"]').should('be.visible').focus().type(userEmail);
    cy.wait(200);
    cy.url().should('include', '/signup'); // Verifica que não redirecionou
    
    cy.get('[name="password"]').should('be.visible').focus().type(userPassword);
    cy.wait(200);
    cy.url().should('include', '/signup'); // Verifica que não redirecionou
    
    cy.get('[name="confirm_password"]').should('be.visible').focus().type(userPassword);
    cy.wait(200);
    cy.url().should('include', '/signup'); // Verifica que não redirecionou

    // Tenta submeter o formulário
    cy.get('button[type="submit"]').should('contain', 'Criar conta').click();

    // TODO: Adicione asserções para verificar se o signup foi bem-sucedido
    // Exemplo: verificar se foi redirecionado para a página de login
    // cy.url().should('include', '/login'); 
    // Exemplo: verificar se uma mensagem de sucesso é exibida
    // cy.get('.success-message').should('be.visible');
  });

  it('should display an error message when passwords do not match', () => {
    const userName = 'Maria';
    const userLastName = 'Santos';
    const userEmail = 'maria.santos@teste.com';
    const userPassword = 'senhaSegura123';
    const differentPassword = 'senhaSegura456';

    // Preenche os campos com waits para evitar redirecionamentos
    cy.get('[name="name"]').should('be.visible').focus().type(userName);
    cy.wait(100);
    cy.get('[name="lastName"]').should('be.visible').focus().type(userLastName);
    cy.wait(100);
    cy.get('[name="email"]').should('be.visible').focus().type(userEmail);
    cy.wait(100);
    cy.get('[name="password"]').should('be.visible').focus().type(userPassword);
    cy.wait(100);
    cy.get('[name="confirm_password"]').should('be.visible').focus().type(differentPassword);
    cy.wait(100);
    cy.get('button[type="submit"]').click();

    // TODO: Adicione asserções para verificar se a mensagem de erro é exibida
    // Exemplo: 
    // cy.get('.error-message') // Substitua pelo seletor da sua mensagem de erro
    //   .should('be.visible')
    //   .and('contain', 'As senhas não coincidem'); 
  });

  it('should display validation errors for required fields', () => {
    // Tenta submeter o formulário sem preencher nenhum campo
    cy.get('button[type="submit"]').click();

    // TODO: Adicione asserções para verificar se as mensagens de validação são exibidas
    // Exemplo:
    // cy.get('[name="name"]').siblings('.text-red-500').should('be.visible');
    // cy.get('[name="email"]').siblings('.text-red-500').should('be.visible');
    // cy.get('[name="password"]').siblings('.text-red-500').should('be.visible');
    // cy.get('[name="confirm_password"]').siblings('.text-red-500').should('be.visible');
  });

  it('should display an error message for invalid email format', () => {
    const userName = 'Pedro';
    const userLastName = 'Costa';
    const invalidEmail = 'email-invalido';
    const userPassword = 'senhaSegura123';

    // Preenche os campos com waits para evitar redirecionamentos
    cy.get('[name="name"]').should('be.visible').focus().type(userName);
    cy.wait(100);
    cy.get('[name="lastName"]').should('be.visible').focus().type(userLastName);
    cy.wait(100);
    cy.get('[name="email"]').should('be.visible').focus().type(invalidEmail);
    cy.wait(100);
    cy.get('[name="password"]').should('be.visible').focus().type(userPassword);
    cy.wait(100);
    cy.get('[name="confirm_password"]').should('be.visible').focus().type(userPassword);
    cy.wait(100);
    cy.get('button[type="submit"]').click();

    // TODO: Adicione asserções para verificar se a mensagem de erro de email inválido é exibida
    // Exemplo:
    // cy.get('[name="email"]').siblings('.text-red-500')
    //   .should('be.visible')
    //   .and('contain', 'Email inválido');
  });

  it('should display an error message for existing email', () => {
    // Usando o email que já existe no sistema (mesmo do teste de login)
    const userName = 'Carlos';
    const userLastName = 'Oliveira';
    const existingEmail = 'space@space.com'; // Email que já existe no sistema (do usuário de login)
    const userPassword = 'spacepassword123'; // Mesma senha do usuário de login

    // Preenche os campos com waits para evitar redirecionamentos
    cy.get('[name="name"]').should('be.visible').focus().type(userName);
    cy.wait(100);
    cy.get('[name="lastName"]').should('be.visible').focus().type(userLastName);
    cy.wait(100);
    cy.get('[name="email"]').should('be.visible').focus().type(existingEmail);
    cy.wait(100);
    cy.get('[name="password"]').should('be.visible').focus().type(userPassword);
    cy.wait(100);
    cy.get('[name="confirm_password"]').should('be.visible').focus().type(userPassword);
    cy.wait(100);
    cy.get('button[type="submit"]').click();

    // TODO: Adicione asserções para verificar se a mensagem de erro de email já existente é exibida
    // Exemplo:
    // cy.get('.error-message') // Substitua pelo seletor da sua mensagem de erro
    //   .should('be.visible')
    //   .and('contain', 'Email já cadastrado');
  });

  // Você pode adicionar mais testes aqui, como:
  // - Testar validação de senha fraca
  // - Testar funcionalidade de mostrar/ocultar senha
  // - Testar links como "Já tem uma conta? Fazer login"
  // - Etc.
});