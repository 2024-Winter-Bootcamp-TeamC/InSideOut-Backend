const express = require('express');
const router = express.Router();

/**
 * @swagger
 * /api/users/hello:
 *   get:
 *     summary: "테스트 API"
 *     description: "테스트용 간단한 API"
 *     responses:
 *       200:
 *         description: "성공"
 */
router.get('/hello', (req, res) => {
  res.status(200).send('Hello, Swagger!');
});

module.exports = router;
