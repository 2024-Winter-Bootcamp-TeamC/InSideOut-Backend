const app = require('./app');

const PORT = app.get('port');
app.listen(PORT, () => {
  console.log(`${PORT}번 포트에서 대기 중`);
});
