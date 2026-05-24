# ==========================================
# STAGE 1: Frontend Asset Compilation Engine
# ==========================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package descriptors first to maximize Docker caching efficiency
COPY ./frontend/package*.json ./

# Install clean production dependencies 
RUN npm ci

# Copy the rest of the frontend source code files
COPY ./frontend/ ./

# Compile your frontend source into optimized static production assets
RUN npm run build


# ==========================================
# STAGE 2: High-Performance Production Nginx
# ==========================================
FROM nginx:1.25-alpine

# Replace default Nginx configuration structures with your custom workspace settings
COPY ./docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Extract only the compiled production code bundle from the builder stage
# (This points to /app/dist for Vite/React or /app/out for Next.js static exports)
COPY --from=builder /app/out /usr/share/nginx/html

# Expose internal standard routing gateway
EXPOSE 80

# Run Nginx in the foreground so the Docker container stays active
CMD ["nginx", "-g", "daemon off;"]
