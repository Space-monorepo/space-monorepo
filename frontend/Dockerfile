# Dockerfile para desenvolvimento
FROM node:18-alpine

WORKDIR /app

# Copia os arquivos de dependências
COPY package.json package-lock.json ./

RUN npm install --force


# Copia o restante do código, exceto arquivos sensíveis ignorados
COPY . .

# Instala googleapis (caso não esteja no package.json)
RUN npm install googleapis

# Copia arquivos sensíveis necessários para o download do .env
COPY service_account.json ./
COPY download-env.js ./

# Baixa o .env do Google Drive
RUN node download-env.js

# Build de produção (agora com todos os arquivos presentes)
RUN npm run build

EXPOSE 3000

# Comando para rodar em modo produção
CMD ["npm", "start"]
