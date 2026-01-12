FROM node:18.19.0-alpine as build

WORKDIR /app

# Install security updates
RUN apk update && apk upgrade && rm -rf /var/cache/apk/*

COPY package*.json ./
RUN npm install --omit=dev

COPY . .
RUN npm run build

FROM nginx:1.25.3-alpine

# Install security updates
RUN apk update && apk upgrade && rm -rf /var/cache/apk/*

COPY --from=build /app/build /usr/share/nginx/html
# Note: nginx.conf is not needed here - nginx:alpine serves static files by default
# The main nginx service in docker-compose.yml handles routing

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]