
# Stage 1: Build the static React compilation layers
FROM node:18-alpine as builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .

# Inject the environment target parameter explicitly into the build sequence
ENV BROWSERSLIST="defaults, not dead"
RUN npm run build

# Stage 2: Serve via Nginx high-performance engine
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
