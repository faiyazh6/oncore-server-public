const express = require('express');
const router = express.Router();
const {
  getNotifications,
  getNotificationById,
  createNotification,
  updateNotification,
  deleteNotification,
  dismissNotification,
  getActiveNotificationCount,
} = require('../controllers/notificationController');

router.get('/notifications', getNotifications);
router.get('/notifications/:id', getNotificationById);
router.post('/notifications', createNotification);
router.put('/notifications/:id', updateNotification);
router.delete('/notifications/:id', deleteNotification);
router.post('/notifications/:id/dismiss', dismissNotification); // Ensure this line is correct
router.get('/notificationCount', getActiveNotificationCount);

module.exports = router;