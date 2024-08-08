const connectDB = require('../config/db');

exports.getTemplateSchedules = async (req, res) => {
  try {
    const db = await connectDB();
    const templateSchedules = await db.collection('template_schedules').find().toArray();
    res.status(200).json({ payload: templateSchedules });
  } catch (error) {
    console.error('Error in getTemplateSchedules:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};