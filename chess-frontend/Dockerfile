# Stage 1: Build the Angular application
FROM node:22-alpine as build

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
# We use npm ci to ensure clean, reproducible builds
COPY package*.json ./
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Build the Angular app for production
# This creates the artifacts in dist/chess-frontend/browser
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Copy our custom Nginx configuration to replace the default one
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built browser artifacts from the build stage to Nginx's serve directory
COPY --from=build /app/dist/chess-frontend/browser /usr/share/nginx/html

# Expose port 80 to the host
EXPOSE 80

# Run Nginx in the foreground so the container doesn't exit
CMD ["nginx", "-g", "daemon off;"]
