import re
src=open('source/site.dc.html').read()
helmet=re.search(r'<helmet>(.*?)</helmet>',src,re.S).group(1)
body=re.search(r'</helmet>(.*)</x-dc>',src,re.S).group(1)
js=re.search(r"data-props=.*?>\n(.*?)</script>",src,re.S).group(1)
body=re.sub(r'<sc-for ([^>]*)>',r'<template data-sc="for" \1>',body).replace('</sc-for>','</template>')
body=re.sub(r'<sc-if ([^>]*)>',r'<template data-sc="if" \1>',body).replace('</sc-if>','</template>')
body=re.sub(r'minmax\((\d+px), 1fr\)',r'minmax(min(\1, 100%), 1fr)',body)
body=body.replace('type="number"','type="text" inputmode="numeric"')
engine=r'''
class DCLogic{constructor(p){this.props=p||{};}setState(o){Object.assign(this.state,o);window.__render();}}
JSCODE
(function(){
const tpl=document.getElementById('tpl');const root=document.getElementById('root');const comp=new Component({});
const get=(sc,path)=>path.trim().split('.').reduce((o,k)=>o==null?undefined:o[k],sc);
const interp=(str,sc)=>str.replace(/\{\{([^}]+)\}\}/g,(m,e)=>{const v=get(sc,e);return v==null?'':String(v);});
const whole=/^\s*\{\{([^}]+)\}\}\s*$/;
function proc(node,sc,out){
 if(node.nodeType===3){out.appendChild(document.createTextNode(interp(node.nodeValue,sc)));return;}
 if(node.nodeType!==1)return;
 if(node.tagName==='TEMPLATE'&&node.dataset.sc){
  if(node.dataset.sc==='for'){const list=get(sc,node.getAttribute('list').match(whole)[1])||[];const as=node.getAttribute('as');
   list.forEach(it=>{const s2=Object.assign({},sc);s2[as]=it;node.content.childNodes.forEach(c=>proc(c,s2,out));});}
  else{const v=get(sc,node.getAttribute('value').match(whole)[1]);if(v)node.content.childNodes.forEach(c=>proc(c,sc,out));}
  return;}
 const el=node.cloneNode(false);let val=null;
 [...node.attributes].forEach(a=>{const n=a.name;const m=a.value.match(whole);
  if(n.startsWith('on')){el.removeAttribute(n);if(m){const f=get(sc,m[1]);if(typeof f==='function')el.addEventListener(n.slice(2),f);}return;}
  if(n.startsWith('hint-')){el.removeAttribute(n);return;}
  if(n==='value'&&(node.tagName==='SELECT'||node.tagName==='INPUT')){val=interp(a.value,sc);}
  el.setAttribute(n,interp(a.value,sc));});
 node.childNodes.forEach(c=>proc(c,sc,el));
 if(val!==null)el.value=val;
 out.appendChild(el);}
window.__render=function(){const ae=document.activeElement;const id=ae&&ae.id;let ss=null;try{ss=ae.selectionStart;}catch(e){}
 const vals=comp.renderVals();const frag=document.createDocumentFragment();tpl.content.childNodes.forEach(c=>proc(c,vals,frag));
 root.replaceChildren(frag);
 if(id){const n=document.getElementById(id);if(n){n.focus({preventScroll:true});try{if(ss!=null)n.setSelectionRange(ss,ss);}catch(e){}}}};
window.__render();})();
'''.replace('JSCODE',js)
html='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Next Owner</title>'''+helmet+'''</head>
<body><div id="root"></div><template id="tpl">'''+body+'''</template>
<script>'''+engine+'''</script></body></html>'''
open('index.html','w').write(html)
