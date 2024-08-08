const express = require('express');
const router = express.Router();
const { getRoiMetrics } = require('../controllers/roiMetricsController');

router.get('/kpi-dashboard', getRoiMetrics);

module.exports = router;