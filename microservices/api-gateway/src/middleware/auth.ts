import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { config } from '../config';

export interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

export const authMiddleware = (req: AuthRequest, res: Response, next: NextFunction): void => {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    res.status(401).json({
      error: 'Unauthorized',
      message: 'No token provided'
    });
    return;
  }

  try {
    const decoded = jwt.verify(token, config.jwt.secret) as any;
    req.user = {
      id: decoded.id,
      email: decoded.email,
      role: decoded.role
    };
    next();
  } catch (error) {
    res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid token'
    });
  }
};

// Generate token (for testing/demo purposes)
export const generateToken = (userId: string, email: string, role: string = 'user'): string => {
  const expiresIn = Number(process.env.JWT_EXPIRES_IN || 3600);
  return jwt.sign(
    { id: userId, email, role },
    config.jwt.secret,
    { expiresIn: expiresIn }
    // { expiresIn: config.jwt.expiresIn }
  );
};
