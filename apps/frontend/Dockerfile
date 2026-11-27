FROM node:22-alpine
WORKDIR /app
RUN chown node:node /app
COPY --chown=node:node package.json package-lock.json ./
USER node
RUN npm ci --ignore-scripts
COPY --chown=node:node index.html tsconfig.json vite.config.ts ./
COPY --chown=node:node src/ ./src/
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
