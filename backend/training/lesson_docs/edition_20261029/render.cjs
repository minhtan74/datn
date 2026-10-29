const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
(async()=>{
 const tasks=JSON.parse(fs.readFileSync(path.join(__dirname,'generated/render-tasks.json'),'utf8'));
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 let cursor=0,done=0;
 try{
  await Promise.all(Array.from({length:3},async()=>{
   const page=await browser.newPage();
   while(cursor<tasks.length){const task=tasks[cursor++];await page.goto(pathToFileURL(task.html).href);
    await page.pdf({path:task.pdf,format:'A4',printBackground:true,preferCSSPageSize:true});
    console.log('PDF',++done,'/',tasks.length,path.basename(task.pdf));}
   await page.close();
  }));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
