FROM node:20-alpine AS builder

WORKDIR /app

COPY apps/admin-pwa/package*.json ./
RUN npm install

COPY apps/admin-pwa .

ARG VITE_AUTH_API_URL
ARG VITE_USER_API_URL
ARG VITE_CONTENT_API_URL
ARG VITE_CATALOG_API_URL
ENV VITE_AUTH_API_URL=${VITE_AUTH_API_URL}
ENV VITE_USER_API_URL=${VITE_USER_API_URL}
ENV VITE_CONTENT_API_URL=${VITE_CONTENT_API_URL}
ENV VITE_CATALOG_API_URL=${VITE_CATALOG_API_URL}

RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app
RUN npm install -g serve@14.2.0

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/public ./public

EXPOSE 4173

CMD ["serve", "-s", "dist", "-l", "4173", "--single"]

