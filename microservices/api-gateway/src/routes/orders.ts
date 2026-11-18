import { Router, Request, Response } from 'express';
import { orderServiceBreaker } from '../middleware/circuitBreaker';
import { config } from '../config';
import { AuthRequest } from '../middleware/auth';

const router = Router();

// Create order
router.post('/', async (req: AuthRequest, res: Response) => {
  try {
    const result = await orderServiceBreaker.fire({
      method: 'POST',
      url: `${config.services.orderService.url}/api/orders`,
      data: {
        ...req.body,
        userId: req.user?.id
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });

    res.status(201).json(result);
  } catch (error: any) {
    res.status(error.response?.status || 500).json({
      error: error.message || 'Failed to create order'
    });
  }
});

// Get orders
router.get('/', async (req: AuthRequest, res: Response) => {
  try {
    const result = await orderServiceBreaker.fire({
      method: 'GET',
      url: `${config.services.orderService.url}/api/orders`,
      params: { userId: req.user?.id }
    });

    res.json(result);
  } catch (error: any) {
    res.status(error.response?.status || 500).json({
      error: error.message || 'Failed to fetch orders'
    });
  }
});

// Get order by ID
router.get('/:orderId', async (req: AuthRequest, res: Response) => {
  try {
    const result = await orderServiceBreaker.fire({
      method: 'GET',
      url: `${config.services.orderService.url}/api/orders/${req.params.orderId}`
    });

    res.json(result);
  } catch (error: any) {
    res.status(error.response?.status || 500).json({
      error: error.message || 'Failed to fetch order'
    });
  }
});

// Cancel order
router.post('/:orderId/cancel', async (req: AuthRequest, res: Response) => {
  try {
    const result = await orderServiceBreaker.fire({
      method: 'POST',
      url: `${config.services.orderService.url}/api/orders/${req.params.orderId}/cancel`,
      data: { userId: req.user?.id }
    });

    res.json(result);
  } catch (error: any) {
    res.status(error.response?.status || 500).json({
      error: error.message || 'Failed to cancel order'
    });
  }
});

export default router;
