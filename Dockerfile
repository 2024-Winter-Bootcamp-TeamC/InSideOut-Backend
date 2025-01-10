# Node.js LTS 버전 사용
FROM node:18-alpine

# 작업 디렉터리 설정
WORKDIR /app

# package.json과 package-lock.json 복사 및 의존성 설치
COPY package.json package-lock.json ./
RUN npm install

# 애플리케이션 소스 코드 복사
COPY . .

# 포트 개방
EXPOSE 3000

# 애플리케이션 실행
CMD ["npm", "start"]
