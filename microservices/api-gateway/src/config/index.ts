import dotenv from 'dotenv';

dotenv.config();

export const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),

  jwt: {
    secret: process.env.JWT_SECRET || 'your-secret-key-change-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h'
  },

  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10), // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10)
  },

  cors: {
    origin: process.env.CORS_ORIGIN || '*'
  },

  services: {
    orderService: {
      url: process.env.ORDER_SERVICE_URL || 'http://localhost:3001',
      timeout: 5000,
      circuitBreaker: {
        timeout: 3000,
        errorThresholdPercentage: 50,
        resetTimeout: 30000
      }
    },
    inventoryService: {
      url: process.env.INVENTORY_SERVICE_URL || 'http://localhost:8001',
      timeout: 5000,
      circuitBreaker: {
        timeout: 3000,
        errorThresholdPercentage: 50,
        resetTimeout: 30000
      }
    },
    notificationService: {
      url: process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:8002',
      timeout: 5000,
      circuitBreaker: {
        timeout: 3000,
        errorThresholdPercentage: 50,
        resetTimeout: 30000
      }
    }
  }
};
