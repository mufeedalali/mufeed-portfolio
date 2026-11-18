import { Request, Response, NextFunction } from 'express';
import { winstonLogger } from './logger';

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  winstonLogger.error({
    error: err.message,
    stack: err.stack,
    method: req.method,
    url: req.url
  });

  const statusCode = (err as any).statusCode || 500;
  const message = err.message || 'Internal Server Error';

  res.status(statusCode).json({
    error: message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};
