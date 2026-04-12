FROM node:18-slim

WORKDIR /app

# Install dependencies
COPY search-ui/ ./
RUN npm install

# Copy source code
COPY . .

# Expose the default React port
EXPOSE 3000

# Start the dev server
CMD ["npm", "start"]
