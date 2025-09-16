# Multi-stage build: build Angular app with Node, serve with nginx
FROM node:18-alpine AS build
WORKDIR /app

# install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --silent || npm install --silent

# copy source and build
COPY . ./
RUN npm run build -- --configuration production

# Stage for using a prebuilt dist directory (copy dist from build context)
FROM nginx:stable-alpine AS prebuilt
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY dist /usr/share/nginx/html

# Default production stage: copy from the build stage output
FROM nginx:stable-alpine AS production
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]