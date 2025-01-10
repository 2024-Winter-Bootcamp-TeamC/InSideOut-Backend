const express = require('express');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const session = require('express-session');
const dotenv = require('dotenv');
const path = require('path');
const { swaggerUi, specs } = require('./src/swagger'); // Swagger 설정 파일 불러오기
//설치한 미들웨어 및 모듈  불러오기

dotenv.config({ path: path.resolve(__dirname, '.env') });

const app = express();
app.set('port',process.env.PORT || 3000);
//app.set('port,포트) : 서버가 실행될 포트 설정

app.use(morgan('dev'));
app.use('/',express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: false}));
app.use(cookieParser(process.env.COOKIE_SECRET));
app.use(session({
    resave: false,
    saveUninitialized: false,
    secret: process.env.COOKIE_SECRET,
    cookie: {
        httpOnly: true,
        secure: false,
    },
    name: 'session-cookie',
}));

// Swagger UI 경로 설정
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));

const userRoutes = require('./src/users/userRoutes'); // 라우트 파일 불러오기

app.use('/api/users', userRoutes); // 라우트 등록


app.use((req, res, next) => {
    console.log('모든 요청에 다 실행됩니다.');
});

app.get('/',(req,res)=>{
    res.send('Hello, Express');
});
/*app.get(주소, 라우터) : 주소에 대한 GET요청이 올 때 어떤 동작을 할지 적는 부분
ex) app.post, app.patch, app.put, app.delete, app.options
express에서는 http와 다르게 res.write, rew.end 대신 res.send 사용
**/

// Express 애플리케이션 객체 내보내기
module.exports = app;