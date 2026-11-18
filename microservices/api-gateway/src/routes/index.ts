import { Router } from 'express';
import rateLimit from 'express-rate-limit';
import { config } from '../config';
import orderRoutes from './orders';
import inventoryRoutes from './inventory';

const router = Router();

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.max,
  message: 'Too many requests from this IP, please try again later.'
});

router.use(limiter);

// Route delegation
router.use('/orders', orderRoutes);
router.use('/inventory', inventoryRoutes);

export default router;
