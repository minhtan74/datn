const { chromium } = require('F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs = require('node:fs');
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  const results = [];
  const groups = [
    ['public', null, ['/', '/login', '/register', '/student/dashboard', '/admin']],
    ['student', 'em.hoang@gmail.com', ['/student/dashboard', '/student/courses', '/student/my-courses', '/student/profile', '/student/progress', '/quiz', '/student/ai-tutor']],
    ['teacher', 'an.nguyen@studyonline.vn', ['/teacher', '/teacher/courses', '/teacher/chapters', '/teacher/lessons', '/teacher/quizzes', '/teacher/reports', '/teacher/documents', '/teacher/profile']],
    ['admin', 'admin@gmail.com', ['/admin', '/admin/users', '/admin/courses', '/admin/payments', '/admin/reports']],
  ];
  for (const [role, email, paths] of groups) {
    const context = await browser.newContext();
    const page = await context.newPage();
    let events = [];
    page.on('pageerror', e => events.push({type:'js', message:e.message}));
    page.on('response', r => {if(r.status() >= 400) events.push({type:'http', status:r.status(), url:r.url()});});
    page.on('requestfailed', r => events.push({type:'network', url:r.url(), error:r.failure()?.errorText}));
    if(email) {
      await page.goto('http://127.0.0.1:5173/login');
      await page.locator('#email').fill(email);
      await page.locator('#password').fill('123456');
      await page.locator('button[type=submit]').click();
      await page.waitForURL(u => !u.pathname.includes('login'), {timeout:15000});
      results.push({role, action:'login', ok:true, events});
    }
    for (const path of paths) {
      events = [];
      await page.goto('http://127.0.0.1:5173'+path);
      await page.waitForTimeout(1200);
      results.push({role, path, viewport:'desktop', url:page.url(), ...await page.evaluate(()=>({chars:document.body.innerText.length, overflow:document.documentElement.scrollWidth>innerWidth, text:document.body.innerText.slice(-1200)})), events});
    }
    await page.setViewportSize({width:390,height:844});
    for(const path of [paths[0], paths[1]]) {
      events=[];
      await page.goto('http://127.0.0.1:5173'+path);
      await page.waitForTimeout(700);
      results.push({role,path,viewport:'mobile', ...await page.evaluate(()=>({chars:document.body.innerText.length,overflow:document.documentElement.scrollWidth>innerWidth})),events});
    }
    await page.screenshot({path:`docs/web-check-${role}.png`,fullPage:true});
    await context.close();
  }
  fs.writeFileSync('docs/web-check-browser.json', JSON.stringify(results,null,2));
  console.log(JSON.stringify(results.map(({text,...r})=>r),null,2));
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
