# Multi-stage build: build Angular app with Node, serve with nginx
FROM node:18-alpine AS build
WORKDIR /app

# install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --silent || npm install --silent

# copy source and build
COPY . ./
RUN npm run build -- --configuration production || npm run build --configuration production

# Production nginx image
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
