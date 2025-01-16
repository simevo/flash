ARG FRONTEND_BASE_IMAGE=deps-frontend-base
ARG VITE_BACKEND_HOST=backend

FROM node:20 AS deps-frontend-base
# Requirements are installed here to ensure they will be cached.
WORKDIR /app
COPY ./package.json ./yarn.lock ./
RUN yarn && yarn cache clean

FROM ${FRONTEND_BASE_IMAGE} AS frontend-builder
WORKDIR /app
COPY index.html vite.config.mts tsconfig*.json env.d.ts eslint.config.js .gitignore .prettierrc.json ./
COPY public ./public
COPY src ./src

FROM frontend-builder AS frontend-built
RUN yarn build

FROM nginx AS frontend
COPY --from=frontend-built /app/dist /usr/share/nginx/html/res
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
