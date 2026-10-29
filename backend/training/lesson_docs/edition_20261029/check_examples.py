"""Execute pure Python/JS examples, syntax-check browser examples, compile Java snippets."""
import json
from pathlib import Path
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
OUT=HERE/'generated'/'code_checks';OUT.mkdir(exist_ok=True)
checks=[]
for source in HERE.glob('*.md'):
    blocks=re.findall(r'```([^\n]*)\n(.*?)\n```',source.read_text(encoding='utf-8'),re.S)
    py=[body for lang,body in blocks if lang=='python']
    if py:
        scope={};exec(compile('\n\n'.join(py),str(source),'exec'),scope)
        if 'test_valid_boundary'in scope:scope['test_valid_boundary']()
        checks.append({'source':source.name,'python_blocks_executed':len(py)})
    for n,(lang,body)in enumerate(blocks):
        if lang=='javascript':
            file=OUT/f'{source.stem}_{n}.mjs';file.write_text(body,encoding='utf-8')
            subprocess.run(['node','--check',str(file)],check=True,capture_output=True)
            runtime=not any(word in body for word in ['document.','fetch(','export '])
            if runtime:
                file.write_text("import assert from 'node:assert/strict';\nconsole.assert = value => assert.ok(value);\n"+body,encoding='utf-8')
                subprocess.run(['node',str(file)],check=True,capture_output=True)
            checks.append({'source':source.name,'block':n,'javascript_syntax':True,'executed':runtime})
        if lang=='java':
            name=f'Example{n}'
            if 'public class Hello'in body:name='Hello';complete=body
            elif body.startswith('final class Product'):name='Product';complete=body
            elif body.startswith('interface PricePolicy'):complete=body
            else:complete='public class '+name+' { public static void main(String[] args) {\n'+body+'\n}}'
            file=OUT/(name+'.java');file.write_text(complete,encoding='utf-8')
            subprocess.run(['javac','-encoding','UTF-8','-d',str(OUT),str(file)],check=True,capture_output=True)
            checks.append({'source':source.name,'block':n,'java_compilation':True})
(HERE/'generated'/'code-validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print('Example validation passed:',len(checks),'checks',flush=True)
