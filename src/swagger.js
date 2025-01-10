const swaggerJSDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

// Swagger 옵션 설정
const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'InsideOut API Documentation',
      version: '1.0.0',
      description: 'InsideOut 백엔드 API 문서',
    },
    servers: [
      {
        url: 'http://localhost:3000', // API 서버 URL
      },
    ],
  },
  apis: ['./src/routes/*.js'], // API 엔드포인트에 대한 주석 파일 경로
};

const specs = swaggerJSDoc(options);

module.exports = { swaggerUi, specs };
