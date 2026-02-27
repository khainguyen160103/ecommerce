# Stage 1: Build
FROM node:20.10-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
COPY next.config.ts tsconfig.json ./
COPY public ./public
COPY src ./src
RUN npm install
RUN npm run build

# Stage 2: Production
FROM node:20.10-alpine

WORKDIR /app

ENV NODE_ENV=production

COPY package.json package-lock.json* ./
COPY next.config.ts tsconfig.json ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
RUN npm install --omit=dev

EXPOSE 3000

CMD ["npm", "start"]