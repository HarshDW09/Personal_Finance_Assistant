# Use multi-stage build for optimized image
FROM python:3.9-slim as backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

FROM node:16 as frontend-build
WORKDIR /app
COPY frontend/ .
RUN npm install
RUN npm run build

FROM nginx:alpine
COPY --from=frontend-build /app/build /usr/share/nginx/html
COPY --from=backend /app /app
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
