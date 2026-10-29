const {chromium}=require('F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs=require('node:fs');
const result={started_at:new Date().toISOString(),questions:[],checks:[]};
const save=()=>fs.writeFileSync('docs/ai-qa-browser-results.json',JSON.stringify(result,null,2));
const assert=(ok,message)=>{if(!ok)throw Error(message)};
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 for(const [role,email] of [['student_em','em.hoang@gmail.com'],['student_phuong','phuong.vu@gmail.com']]){
  const context=await browser.newContext();const page=await context.newPage();page.setDefaultTimeout(15000);
  let conv=null,events=[];page.on('dialog',d=>d.accept());page.on('pageerror',e=>events.push(e.message));
  try{
   await page.goto('http://127.0.0.1:5173/login',{waitUntil:'domcontentloaded'});
   await page.locator('#email').fill(email);await page.locator('#password').fill('123456');await page.locator('button[type=submit]').click();await page.waitForURL(u=>u.pathname!='/login');
   await page.goto('http://127.0.0.1:5173/student/ai-tutor',{waitUntil:'domcontentloaded'});
   const select=page.locator('main select');await select.locator('option[value="1"]').waitFor({state:'attached'});
   await select.selectOption('1');await page.waitForTimeout(350);
   result.checks.push({role,name:'Đăng nhập và chọn khóa Python',passed:true});save();
   const questions=[['common','Vòng lặp for và while trong Python khác nhau thế nào?'],['followup','Cho tôi một ví dụ về vòng lặp vừa nói.'],['outside','Ai vô địch World Cup năm 2018?']];
   for(const [kind,question]of questions){
    const input=page.locator('main form input');await input.fill(question);const start=Date.now();
    const pending=page.waitForResponse(r=>r.url().endsWith('/api/ai/chat')&&r.request().method()==='POST',{timeout:210000});
    await page.getByRole('button',{name:'Gửi',exact:true}).click();
    const disabledDuring=await input.isDisabled();
    const response=await pending;const body=await response.json();const d=body.data||{};
    assert(response.status()===200&&d.answer,JSON.stringify(body));
    const previous=conv;conv=d.conversation_id;
    await page.waitForFunction(answer=>document.querySelector('.ai-tutor-chat')?.innerText.includes(answer),d.answer);
    const chat=await page.locator('.ai-tutor-chat').innerText();
    result.questions.push({id:`ui-${role}-${kind}`,kind,role,question,course_id:1,answer:d.answer,sources:d.sources,used_context:d.used_context,conversation_id:conv,status:response.status(),ms:Date.now()-start,fallback:d.answer.includes('tạm gián đoạn'),refused:d.answer.includes('không tìm thấy thông tin phù hợp'),input_disabled_while_waiting:disabledDuring,same_conversation:!previous||previous===conv,literal_markdown_fences:chat.includes('```')});save();
    console.log(role,kind,response.status(),Date.now()-start);
    if(kind==='followup')await page.screenshot({path:`docs/ai-qa-${role}-chat.png`,fullPage:true});
   }
   await page.getByRole('button',{name:/Cuộc trò chuyện mới/}).click();
   assert((await page.locator('.ai-tutor-chat').innerText()).includes('Xin chào!'),'Khung chat không reset');
   await page.reload({waitUntil:'domcontentloaded'});
   await select.locator('option[value="1"]').waitFor({state:'attached'});await select.selectOption('1');
   const sidebar=page.locator('main .s-card-body').first();
   await sidebar.getByText(questions[0][1],{exact:false}).first().click();
   await page.waitForFunction(q=>document.querySelector('.ai-tutor-chat')?.innerText.includes(q),questions[2][1]);
   result.checks.push({role,name:'Hỏi nối tiếp giữ hội thoại, tạo mới reset khung và tải lại đọc đủ lịch sử',passed:result.questions.filter(x=>x.role===role).every(x=>x.same_conversation)});
   if(role==='student_phuong'){
    await page.setViewportSize({width:390,height:844});await page.waitForTimeout(300);
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
    result.checks.push({role,name:'Chat mobile không tràn ngang',passed:!overflow,overflow});
    await page.screenshot({path:'docs/ai-qa-mobile.png',fullPage:true});await page.setViewportSize({width:1280,height:720});
   }
   const removed=page.waitForResponse(r=>r.url().endsWith('/api/ai/conversations/'+conv)&&r.request().method()==='DELETE');
   await sidebar.locator('div').filter({has:page.getByText(questions[0][1],{exact:false})}).locator('span[title="Xóa"]').last().click();
   const r=await removed;assert(r.status()===200,'Xóa hội thoại thất bại');conv=null;
   result.checks.push({role,name:'Xóa hội thoại bằng giao diện',passed:true});
  }catch(e){result.checks.push({role,name:'Luồng hỏi đáp UI',passed:false,error:e.message});await page.screenshot({path:`docs/ai-qa-ui-error-${role}.png`,fullPage:true}).catch(()=>{});}
  finally{
   if(conv){const token=await page.evaluate(()=>localStorage.getItem('token'));const r=await context.request.delete('http://127.0.0.1:8080/api/ai/conversations/'+conv,{headers:{Authorization:'Bearer '+token}});result.checks.push({role,name:'Dọn hội thoại còn lại bằng API',passed:r.status()===200});}
   result.checks.push({role,name:'Không có JavaScript exception',passed:events.length===0,events});save();await context.close();
  }
 }
 result.finished_at=new Date().toISOString();save();await browser.close();console.log('COMPLETE',result.questions.length,'questions',result.checks.length,'checks');
})().catch(e=>{console.error(e);save();process.exit(1)});
