FROM node:20-alpine AS builder

WORKDIR /app

COPY apps/client-web/package*.json ./
RUN npm install

COPY apps/client-web .

ARG NEXT_PUBLIC_CATALOG_API_URL
ARG NEXT_PUBLIC_CONTENT_API_URL
ENV NEXT_PUBLIC_CATALOG_API_URL=${NEXT_PUBLIC_CATALOG_API_URL}
ENV NEXT_PUBLIC_CONTENT_API_URL=${NEXT_PUBLIC_CONTENT_API_URL}

RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/next.config.mjs ./next.config.mjs
COPY --from=builder /app/tsconfig.json ./tsconfig.json

EXPOSE 3000

CMD ["npm", "run", "start"]

