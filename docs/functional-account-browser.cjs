const { chromium } = require('F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs = require('node:fs');
const state = JSON.parse(fs.readFileSync('docs/functional-account-state.json','utf8'));
const results=process.env.AUDIT_RETRY ? JSON.parse(fs.readFileSync('docs/functional-account-browser.json','utf8')) : [];
const save=()=>fs.writeFileSync('docs/functional-account-browser.json',JSON.stringify(results,null,2));
const assert=(x,msg)=>{if(!x)throw Error(msg)};
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 for(const [role,email] of Object.entries(state.accounts)){
  if(process.env.AUDIT_ROLES && !process.env.AUDIT_ROLES.split(',').includes(role))continue;
  const context=await browser.newContext({acceptDownloads:true});
  const page=await context.newPage();page.setDefaultTimeout(12000);
  page.on('dialog',d=>d.accept());
  let events=[];
  page.on('pageerror',e=>events.push({type:'js',message:e.message}));
  page.on('response',r=>{if(r.status()>=400)events.push({type:'http',status:r.status(),url:r.url()})});
  async function step(name,fn){
   events=[];const start=Date.now();
   try{const data=await fn();results.push({role,name,passed:true,ms:Date.now()-start,data,events});}
   catch(e){results.push({role,name,passed:false,ms:Date.now()-start,error:e.message,events});await page.screenshot({path:`docs/functional-failure-${role}-${results.length}.png`,fullPage:true}).catch(()=>{});}
   save();console.log(role,name,results.at(-1).passed?'PASS':'FAIL');
  }
  const go=async path=>{await page.goto('http://127.0.0.1:5173'+path,{waitUntil:'domcontentloaded'});};
  await step('Đăng nhập bằng form',async()=>{
   await go('/login');await page.locator('#email').fill(email);await page.locator('#password').fill('123456');
   await page.locator('button[type=submit]').click();await page.waitForURL(u=>u.pathname!='/login');return {url:page.url()};
  });
  if(role.startsWith('teacher') && !process.env.AUDIT_LOGOUT_ONLY){
   const cid=role==='teacher_an'?state.course_id:state.fixture_courses[1];
   await step('Sửa mô tả khóa test qua giao diện',async()=>{
    await go('/teacher/courses');const row=page.locator('.course-dash-card').filter({hasText:state.run+' '+role});await row.waitFor();
    await row.getByRole('button',{name:'✏️',exact:true}).click();
    const form=page.locator('form').filter({has:page.locator('textarea')});
    await form.locator('textarea').fill('Mô tả được cập nhật qua giao diện trong lượt kiểm thử '+state.run);
    const res=page.waitForResponse(r=>r.url().includes('/api/courses')&&r.request().method()==='PUT');
    await form.getByRole('button',{name:'Lưu lại'}).click();const r=await res;assert(r.status()===200,'Không lưu được khóa');return {status:r.status(),course_id:cid};
   });
   await step('Lọc khóa học theo tên',async()=>{
    const input=page.locator('input[type=text]').first();await input.fill(state.run);await page.waitForTimeout(300);
    const rows=await page.locator('.course-dash-card').count();assert(rows>=1,'Không tìm thấy khóa test');return {visible_rows:rows};
   });
   await step('Mở báo cáo giảng viên',async()=>{await go('/teacher/reports');await page.waitForTimeout(700);assert((await page.locator('body').innerText()).length>500,'Trang trống');await page.screenshot({path:`docs/functional-${role}-reports.png`,fullPage:true});return {overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)};});
  }
  if(role.startsWith('student') && !process.env.AUDIT_LOGOUT_ONLY){
   await step('Xem chi tiết khóa và đăng ký miễn phí',async()=>{
    await go('/student/courses');const card=page.locator('#card-'+state.course_id);await card.waitFor();
    await card.getByRole('button',{name:/Xem chi tiết/}).click();assert(await page.locator('#detailModal').isVisible(),'Không mở chi tiết');
    const response=page.waitForResponse(r=>r.url().includes('/api/enrollments')&&r.request().method()==='POST');
    await page.locator('#detailModal').getByRole('button',{name:/Đăng ký miễn phí/}).click();const r=await response;
    assert(r.status()===200,'Đăng ký không thành công');return {course_id:state.course_id,status:r.status()};
   });
   for(const [i,id] of state.lessons.entries())await step('Học bài và đánh dấu hoàn thành '+(i+1),async()=>{
    await go('/lesson?id='+id);await page.locator('#markDoneBtn').waitFor();
    const res=page.waitForResponse(r=>r.url().includes('/api/progress')&&r.request().method()==='POST');await page.locator('#markDoneBtn').click();
    const r=await res;assert(r.status()===200,'Lưu tiến độ thất bại');await page.locator('#completedBadge').waitFor();
    await page.reload({waitUntil:'domcontentloaded'});await page.locator('#completedBadge').waitFor();return {lesson_id:id,persisted_after_reload:true};
   });
   for(const correctCount of [0,3,6])await step(`Làm quiz và nộp ${correctCount}/6 câu đúng`,async()=>{
    let res=page.waitForResponse(r=>r.url().includes('/api/quizzes/questions?')&&r.status()===200);await go('/quiz-show?id='+state.quiz_id);let opened=await (await res).json();
    assert(opened.data.length===6,'Đề không có đủ 6 câu');assert(opened.data.every(q=>!('correct_answer'in q)),'Lộ đáp án trước nộp');
    await page.locator('.question-card').first().waitFor();
    const first=opened.data[0];const firstKey='ABCD'.split('').find(k=>first['option_'+k.toLowerCase()]!==state.correct_values[String(first.id)]);
    await page.locator(`label[for=q${first.id}_${firstKey}]`).click();
    if(correctCount===0){
     res=page.waitForResponse(r=>r.url().includes('/api/quizzes/questions?')&&r.status()===200);await page.reload({waitUntil:'domcontentloaded'});const reload=await(await res).json();
     assert(reload.attempt_token===opened.attempt_token,'Tải lại tạo lượt mới');assert(JSON.stringify(reload.data)===JSON.stringify(opened.data),'Đảo lại phương án khi reload');
     await page.waitForFunction(({id,key})=>document.querySelector(`#q${id}_${key}`)?.checked,{id:first.id,key:firstKey});
    }
    for(const [i,q]of opened.data.entries()){
     const key='ABCD'.split('').find(k=>q['option_'+k.toLowerCase()] && ((q['option_'+k.toLowerCase()]===state.correct_values[String(q.id)]) === (i<correctCount)));
     assert(key,'Không tìm được phương án');await page.locator(`label[for=q${q.id}_${key}]`).click();
    }
    const submitted=page.waitForResponse(r=>r.url().includes('/api/quizzes/submit')&&r.request().method()==='POST');
    await page.getByRole('button',{name:/Nộp bài/}).click();const r=await submitted;const b=await r.json();
    assert(r.status()===200,JSON.stringify(b));assert(b.percent===correctCount/6*100,'Sai điểm: '+b.percent);assert(b.passed===(correctCount>=5),'Sai điều kiện đạt');
    await page.waitForURL(u=>u.pathname==='/student/quiz-result');await page.waitForTimeout(400);
    const immediateText=await page.locator('body').innerText();
    await page.screenshot({path:`docs/functional-${role}-score-${b.percent}.png`,fullPage:true});
    await go('/student/quiz-result?result_id='+b.result_id);await page.waitForTimeout(500);
    return {score:b.score,total:b.total,percent:b.percent,passed:b.passed,result_id:b.result_id,attempts_left:b.attempts_left,answers_revealed:b.answers_revealed,reload_same_attempt:correctCount===0,displayed_result:immediateText.slice(0,1000)};
   });
   await step('Kiểm tra tiến độ và gợi ý sau khi làm bài',async()=>{await go('/student/progress?course_id='+state.course_id);await page.waitForTimeout(700);await page.screenshot({path:`docs/functional-${role}-progress.png`,fullPage:true});return {text:(await page.locator('body').innerText()).slice(-3500)};});
   await step('Trang tiến độ trên điện thoại',async()=>{await page.setViewportSize({width:390,height:844});await page.waitForTimeout(300);const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);assert(!overflow,'Tràn ngang');await page.screenshot({path:`docs/functional-${role}-mobile.png`,fullPage:true});return {width:390,overflow};});
  }
  if(role==='admin' && !process.env.AUDIT_LOGOUT_ONLY){
   await step('Tìm người dùng theo email',async()=>{await go('/admin/users');const input=page.locator('input[type=text]').first();await input.fill('em.hoang@gmail.com');await page.waitForTimeout(500);const text=await page.locator('tbody').innerText();assert(text.includes('em.hoang@gmail.com'),'Không tìm được học viên');return {text};});
   await step('Xuất CSV từ giao diện báo cáo',async()=>{await go('/admin/reports');const btn=page.getByRole('button',{name:/Xuất CSV/}).first();await btn.waitFor();const downloaded=page.waitForEvent('download');await btn.click();const d=await downloaded;await d.saveAs('docs/functional-ui-export.csv');return {filename:d.suggestedFilename()};});
   await step('Xem giao dịch và số liệu admin',async()=>{await go('/admin/payments');await page.waitForTimeout(600);await page.screenshot({path:'docs/functional-admin-payments.png',fullPage:true});return {text:(await page.locator('body').innerText()).slice(0,1600)};});
  }
  await step('Đăng xuất và chặn quay lại trang riêng',async()=>{
   await page.setViewportSize({width:1280,height:720});
   const logout=page.getByRole('button',{name:/Đăng xuất/}).first();
   if(await logout.count()) await logout.click();else await page.getByRole('link',{name:/Đăng xuất/}).first().click();
   await go(role==='admin'?'/admin':role.startsWith('teacher')?'/teacher':'/student/dashboard');await page.waitForURL(u=>u.pathname==='/login');return {url:page.url()};
  });
  await context.close();
 }
 await browser.close();save();console.log('TOTAL',results.length,'FAIL',results.filter(x=>!x.passed).length);
})().catch(e=>{console.error(e);save();process.exit(1)});
