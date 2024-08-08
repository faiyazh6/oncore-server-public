const Notification = require('../models/Notification');
const { broadcast } = require('../websocket');

// Get all notifications
const getNotifications = async (req, res) => {
  try {
    const notifications = await Notification.find();
    res.status(200).json(notifications);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// Get a specific notification by ID
const getNotificationById = async (req, res) => {
  try {
    const notification = await Notification.findById(req.params.id);
    if (!notification) {
      return res.status(404).json({ message: 'Notification not found' });
    }
    res.status(200).json(notification);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// Create a new notification
const createNotification = async (req, res) => {
  const notification = new Notification({
    notification_name: req.body.notification_name,
    description: req.body.description,
    person_id: req.body.person_id,
    importance: req.body.importance,
    time: req.body.time,
    icon: req.body.icon,
    active: req.body.active,
  });

  try {
    const newNotification = await notification.save();
    res.status(201).json(newNotification);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
};

// Dismiss a notification (set active to false)
const dismissNotification = async (req, res) => {
  try {
    const notification = await Notification.findById(req.params.id);
    if (!notification) {
      return res.status(404).json({ message: 'Notification not found' });
    }
    notification.active = false;
    await notification.save();

    // Send the response first
    res.status(200).json(notification);

    // Perform the broadcast after sending the response
    setTimeout(async () => {
      try {
        const count = await Notification.countDocuments({ active: true });
        broadcast({ type: 'NOTIFICATION_COUNT', count });
      } catch (error) {
        console.error('Error broadcasting notification count:', error);
      }
    }, 0);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// Delete a notification by ID
const deleteNotification = async (req, res) => {
  try {
    const notification = await Notification.findById(req.params.id);
    if (!notification) {
      return res.status(404).json({ message: 'Notification not found' });
    }
    await notification.remove();
    res.status(200).json({ message: 'Notification deleted' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// Update a notification
const updateNotification = async (req, res) => {
  try {
    const notification = await Notification.findById(req.params.id);
    if (!notification) {
      return res.status(404).json({ message: 'Notification not found' });
    }

    notification.notification_name = req.body.notification_name || notification.notification_name;
    notification.description = req.body.description || notification.description;
    notification.person_id = req.body.person_id || notification.person_id;
    notification.importance = req.body.importance || notification.importance;
    notification.time = req.body.time || notification.time;
    notification.icon = req.body.icon || notification.icon;
    notification.active = req.body.active !== undefined ? req.body.active : notification.active;

    const updatedNotification = await notification.save();
    res.status(200).json(updatedNotification);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
};

const getActiveNotificationCount = async (req, res) => {
  try {
    const count = await Notification.countDocuments({ active: true });
    res.status(200).json({ count });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};



module.exports = {
  getActiveNotificationCount,
  getNotifications,
  getNotificationById,
  createNotification,
  updateNotification,
  deleteNotification,
  dismissNotification,
};