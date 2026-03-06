FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install git securely (needed if the app relies on git operations)
RUN apk add --no-cache git

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application source
COPY . .

# Build the application (if there is a build step, usually for TS)
# Attempt to run build script if it exists, otherwise ignore
RUN npm run build --if-present

# Expose the standard port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
