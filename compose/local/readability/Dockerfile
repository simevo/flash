FROM node:22

WORKDIR /app

COPY package.json yarn.lock index.js /app/

RUN yarn install && yarn cache clean

EXPOSE 8081

CMD ["node", "index.js"]
