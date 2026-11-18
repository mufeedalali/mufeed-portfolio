import CircuitBreaker from 'opossum';
import axios, { AxiosRequestConfig } from 'axios';
import { config } from '../config';

interface ServiceConfig {
  url: string;
  timeout: number;
  circuitBreaker: {
    timeout: number;
    errorThresholdPercentage: number;
    resetTimeout: number;
  };
}

const createCircuitBreaker = (serviceConfig: ServiceConfig) => {
  const breaker = new CircuitBreaker(
    async (requestConfig: AxiosRequestConfig) => {
      const response = await axios({
        ...requestConfig,
        timeout: serviceConfig.timeout
      });
      return response.data;
    },
    {
      timeout: serviceConfig.circuitBreaker.timeout,
      errorThresholdPercentage: serviceConfig.circuitBreaker.errorThresholdPercentage,
      resetTimeout: serviceConfig.circuitBreaker.resetTimeout
    }
  );

  breaker.on('open', () => {
    console.warn(`Circuit breaker opened for ${serviceConfig.url}`);
  });

  breaker.on('halfOpen', () => {
    console.info(`Circuit breaker half-open for ${serviceConfig.url}`);
  });

  breaker.on('close', () => {
    console.info(`Circuit breaker closed for ${serviceConfig.url}`);
  });

  return breaker;
};

export const orderServiceBreaker = createCircuitBreaker(config.services.orderService);
export const inventoryServiceBreaker = createCircuitBreaker(config.services.inventoryService);
export const notificationServiceBreaker = createCircuitBreaker(config.services.notificationService);
