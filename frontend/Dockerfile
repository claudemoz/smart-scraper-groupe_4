# Stage 1: Build de l'application React
FROM node:18-alpine as build

# Définir le répertoire de travail
WORKDIR /app

# Argument de build pour l'URL de l'API
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer toutes les dépendances (y compris devDependencies pour le build)
RUN npm ci
# RUN npm ci --only=production

COPY . .

RUN npm run build

FROM nginx:alpine

# Installer curl pour le healthcheck
RUN apk add --no-cache curl

# Copier la configuration Nginx personnalisée
COPY nginx.conf /etc/nginx/nginx.conf

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
