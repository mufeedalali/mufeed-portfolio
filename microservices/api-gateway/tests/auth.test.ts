import { generateToken } from '../src/middleware/auth';
import jwt from 'jsonwebtoken';

describe('Auth Middleware', () => {
  const JWT_SECRET = 'test-secret';

  beforeAll(() => {
    process.env.JWT_SECRET = JWT_SECRET;
  });

  describe('generateToken', () => {
    it('should generate a valid JWT token', () => {
      const userId = 'user123';
      const email = 'test@example.com';
      const role = 'user';

      const token = generateToken(userId, email, role);
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');

      const decoded = jwt.verify(token, JWT_SECRET) as any;
      expect(decoded.id).toBe(userId);
      expect(decoded.email).toBe(email);
      expect(decoded.role).toBe(role);
    });

    it('should use default role if not provided', () => {
      const token = generateToken('user123', 'test@example.com');
      const decoded = jwt.verify(token, JWT_SECRET) as any;
      expect(decoded.role).toBe('user');
    });
  });
});
