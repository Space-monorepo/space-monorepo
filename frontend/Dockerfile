# Etapa de build
FROM node:18-alpine AS builder

WORKDIR /app

# Copia apenas os arquivos necessários para o build
COPY package.json package-lock.json ./

RUN npm install

COPY . .

# Gera o build de produção
RUN npm run build

# Etapa de runtime
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

# Copia só o necessário do builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["npm", "start"]
