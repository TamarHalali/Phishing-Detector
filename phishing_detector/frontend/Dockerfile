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
COPY ../nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]