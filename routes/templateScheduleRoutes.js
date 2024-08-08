const express = require('express');
const router = express.Router();
const { getTemplateSchedules } = require('../controllers/templateScheduleController');

router.get('/template-schedules', getTemplateSchedules);

module.exports = router;