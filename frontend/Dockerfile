# Dockerfile para desenvolvimento
FROM node:18-alpine

WORKDIR /app

# Copia os arquivos de dependências
COPY package.json package-lock.json ./

RUN npm install --force

# Copia todo o código para dentro do container (após instalar dependências)
COPY . .

# Build de produção (agora com todos os arquivos presentes)
RUN npm run build

EXPOSE 3000

# Comando para rodar em modo produção
CMD ["npm", "start"]
