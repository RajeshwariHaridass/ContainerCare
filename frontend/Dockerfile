# ==============================================================================
# ContainerCare Frontend Dockerfile
# Stage 1: Build production React application with Vite
# Stage 2: Serve via Nginx with API reverse proxy
# ==============================================================================

# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Production Nginx Server
FROM nginx:alpine

# Copy Nginx configuration with reverse proxy support for /api
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
