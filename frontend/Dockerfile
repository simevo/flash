ARG FRONTEND_BASE_IMAGE=deps-frontend-base
ARG VITE_BACKEND_HOST=backend

FROM node:22 AS deps-frontend-base
# Requirements are installed here to ensure they will be cached.
WORKDIR /app
COPY ./package.json ./yarn.lock ./
RUN yarn && yarn cache clean
RUN yarn playwright install --with-deps

FROM ${FRONTEND_BASE_IMAGE} AS frontend-builder
WORKDIR /app
COPY \
    .gitignore \
    .prettierrc.json \
    env.d.ts \
    eslint.config.ts \
    index.html \
    playwright.config.ts \
    tsconfig*.json \
    vite.config.mts \
    vitest.config.mts \
    ./
COPY e2e ./e2e
COPY src ./src
COPY public ./public

FROM frontend-builder AS frontend-built
RUN yarn build

FROM nginx AS frontend
COPY --from=frontend-built /app/dist /usr/share/nginx/html/res
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
