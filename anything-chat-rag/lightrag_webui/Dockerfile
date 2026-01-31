# LightRAG WebUI Dockerfile
FROM node:20-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Development/Production image (using dev mode)
FROM base AS runner
WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy dependencies and source code
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NODE_ENV=development
ENV PORT=5173
ENV HOST=0.0.0.0

EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5173/ || exit 1

# Run dev server
CMD ["npm", "run", "dev-no-bun"]

