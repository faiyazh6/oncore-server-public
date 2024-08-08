const errorHandler = (err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ errorMessage: 'Server error' });
  };
  
  module.exports = errorHandler;