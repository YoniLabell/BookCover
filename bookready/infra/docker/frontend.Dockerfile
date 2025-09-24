FROM node:18-alpine

WORKDIR /app
COPY frontend/package.json frontend/tailwind.config.ts frontend/postcss.config.js frontend/tsconfig.json /app/
RUN npm install
COPY frontend /app
RUN npm run build

CMD ["npm", "start"]
