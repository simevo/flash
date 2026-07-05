FROM node:24

WORKDIR /app

COPY package.json yarn.lock index.js /app/

RUN yarn install && yarn cache clean

EXPOSE 8081

CMD ["node", "index.js"]
