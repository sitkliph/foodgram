FROM node:21.7.1-alpine
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
