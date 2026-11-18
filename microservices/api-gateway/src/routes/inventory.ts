import { Router, Response } from 'express';
import { inventoryServiceBreaker } from '../middleware/circuitBreaker';
import { config } from '../config';
import { AuthRequest } from '../middleware/auth';

const router = Router();

// Get inventory
router.get('/', async (req: AuthRequest, res: Response) => {
  try {
    const result = await inventoryServiceBreaker.fire({
      method: 'GET',
      url: `${config.services.inventoryService.url}/api/inventory`,
      params: req.query
    });

    res.json(result);
  } catch (error: any) {
    res.status(error.response?.status || 500).json({
      error: error.message || 'Failed to fetch inventory'
    });
  }
});

// Get product inventory
router.get('/:productId', async (req: AuthRequest, res: Response) => {
  try {
    const result = await inventoryServiceBreaker.fire({
      method: 'GET',
      url: `${config.services.inventoryService.url}/api/inventory/${req.params.productId}`
    });

    res.json(result);
  } catch (error: any) {
    res.status(error.response?.status || 500).json({
      error: error.message || 'Failed to fetch product inventory'
    });
  }
});

// Update stock (admin only)
router.post('/:productId/stock', async (req: AuthRequest, res: Response) => {
  if (req.user?.role !== 'admin') {
    res.status(403).json({ error: 'Forbidden: Admin access required' });
    return;
  }

  try {
    const result = await inventoryServiceBreaker.fire({
      method: 'POST',
      url: `${config.services.inventoryService.url}/api/inventory/${req.params.productId}/stock`,
      data: req.body
    });

    res.json(result);
  } catch (error: any) {
    res.status(error.response?.status || 500).json({
      error: error.message || 'Failed to update stock'
    });
  }
});

export default router;
