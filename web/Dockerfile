# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm install --frozen-lockfile || npm install

COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app .
EXPOSE 3000

CMD ["npm", "start"]
