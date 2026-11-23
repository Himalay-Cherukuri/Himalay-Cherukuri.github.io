/* Shared site behaviour: theme, drawer, sidebar tree, scroll-spy, copy links, search, shortcuts. */
(function(){
  "use strict";
  var body=document.body, root=body.dataset.root||"", sec=body.dataset.section||"";
  var secRoot=body.dataset.secroot||"";
  function $(s,c){return (c||document).querySelector(s)}
  function $$(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s))}
  function store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}

  // 1. theme
  var tbtn=$("#theme-toggle");
  function curTheme(){return document.documentElement.dataset.theme||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light")}
  function paintBtn(){if(tbtn){var d=curTheme()==="dark";tbtn.textContent=d?"☀":"☾";tbtn.setAttribute("aria-label",d?"Switch to light theme":"Switch to dark theme")}}
  if(tbtn){tbtn.addEventListener("click",function(){var n=curTheme()==="dark"?"light":"dark";document.documentElement.dataset.theme=n;store("theme",n);paintBtn()});paintBtn()}

  // 2. drawer + tree
  var mbtn=$("#menu-btn");
  if(mbtn){mbtn.addEventListener("click",function(){var o=body.classList.toggle("drawer-open");mbtn.setAttribute("aria-expanded",o)});
    var bd=$(".backdrop");if(bd)bd.addEventListener("click",function(){body.classList.remove("drawer-open");mbtn.setAttribute("aria-expanded","false")})}
  document.addEventListener("keydown",function(e){if(e.key==="Escape"&&body.classList.contains("drawer-open")){body.classList.remove("drawer-open");if(mbtn)mbtn.focus()}});
  var openKey="open:"+sec, openSet={};
  try{openSet=JSON.parse(store(openKey)||"{}")}catch(e){}
  $$(".tree > li.book").forEach(function(li){
    var b=li.querySelector("button"),id=li.dataset.id;
    if(openSet[id])li.classList.add("is-open");
    b.setAttribute("aria-expanded",li.classList.contains("is-open"));
    b.addEventListener("click",function(){var o=li.classList.toggle("is-open");b.setAttribute("aria-expanded",o);openSet[id]=o;store(openKey,JSON.stringify(openSet))});
  });
  var cur=$(".tree li.is-current");if(cur&&cur.scrollIntoView){var sb=$(".sidebar");if(sb)sb.scrollTop=cur.offsetTop-sb.clientHeight/3}

  // 3. scroll-spy
  var tocLinks=$$(".toc a");
  if(tocLinks.length&&"IntersectionObserver" in window){
    var map={};tocLinks.forEach(function(a){map[decodeURIComponent(a.hash.slice(1))]=a});
    var secs=Object.keys(map).map(function(id){return document.getElementById(id)}).filter(Boolean);
    var vis={};
    var io=new IntersectionObserver(function(es){es.forEach(function(e){vis[e.target.id]=e.isIntersecting});
      var first=secs.find?secs.find(function(s){return vis[s.id]}):null;
      if(first){tocLinks.forEach(function(a){a.classList.remove("active")});var a=map[first.id];a.classList.add("active");
        var col=$(".toc-col");if(col&&(a.offsetTop<col.scrollTop||a.offsetTop>col.scrollTop+col.clientHeight-40))col.scrollTop=a.offsetTop-80}},{rootMargin:"-60px 0px -60% 0px"});
    secs.forEach(function(s){io.observe(s)});
  }

  // 4. copy deep link
  var toast=document.createElement("div");toast.className="toast";toast.setAttribute("role","status");body.appendChild(toast);
  function say(m){toast.textContent=m;toast.classList.add("show");clearTimeout(say.t);say.t=setTimeout(function(){toast.classList.remove("show")},1600)}
  document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a.para-id, a.verse-num");if(!a)return;
    var url=location.href.split("#")[0]+a.getAttribute("href");
    if(navigator.clipboard){e.preventDefault();history.replaceState(null,"",a.getAttribute("href"));navigator.clipboard.writeText(url).then(function(){say("Link copied")},function(){say(url)})}});

  // 7. show tags toggle
  var tagBtn=$("#tags-toggle");
  if(tagBtn){if(store("showTags")==="1"){body.classList.add("show-tags");tagBtn.setAttribute("aria-pressed","true")}
    tagBtn.addEventListener("click",function(){var o=body.classList.toggle("show-tags");tagBtn.setAttribute("aria-pressed",o);store("showTags",o?"1":"0")})}
  var cBtn=$("#comm-toggle");
  if(cBtn){cBtn.addEventListener("click",function(){var ds=$$("details.comm"),anyOpen=ds.some(function(d){return d.open});ds.forEach(function(d){d.open=!anyOpen});cBtn.textContent=anyOpen?"Expand all commentary":"Collapse all commentary"})}

  // 6. shortcuts
  document.addEventListener("keydown",function(e){
    var t=e.target.tagName;if(t==="INPUT"||t==="TEXTAREA"||e.metaKey||e.ctrlKey||e.altKey)return;
    if(e.key==="/"){var i=$(".header-search input")||$("#q");if(i){e.preventDefault();i.focus()}}
    else if(e.key==="["){var p=$("a[rel=prev]");if(p)location.href=p.href}
    else if(e.key==="]"){var n=$("a[rel=next]");if(n)location.href=n.href}
  });

  // 8. :target highlight on load handled by CSS; ensure details opened
  function openTarget(){if(!location.hash)return;var el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(!el)return;var d=el.closest&&el.closest("details");if(d)d.open=true}
  openTarget();window.addEventListener("hashchange",openTarget);

  // 5. search
  function norm(s){return (s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase()}
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  var idx=null,loading=null;
  function load(){if(idx)return Promise.resolve(idx);if(loading)return loading;
    loading=fetch(secRoot+"search_index.json").then(function(r){return r.json()}).then(function(d){d.forEach(function(x){x.n=norm(x.t)});idx=d;return d});return loading}
  var hs=$(".header-search input");if(hs&&sec!=="mahabharata")hs.addEventListener("focus",load,{once:true});
  function snippet(t,terms){var n=norm(t),pos=n.indexOf(terms[0]);var s=Math.max(0,pos-80),e=Math.min(t.length,(pos<0?0:pos)+220);
    var out=(s>0?"…":"")+t.slice(s,e)+(e<t.length?"…":"");var h=esc(out);
    terms.forEach(function(w){if(!w)return;var re=new RegExp("("+w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+")","gi");h=h.replace(re,"<mark>$1</mark>")});return h}
  var q=$("#q"),res=$("#results"),st=$("#search-status");
  var smeta=$("#shard-meta");
  if(q&&res&&smeta){
    // sharded search (Mahabharata): one JSON index per parva, loaded on demand
    var meta=JSON.parse(smeta.textContent),cache={},sel=$("#shard"),gen=0;
    var normD=function(s){return norm(s).replace(/[\u200c\u200d\u0964\u0965]/g,"")};
    var getShard=function(m){if(cache[m.id])return Promise.resolve(cache[m.id]);
      return fetch(m.f).then(function(r){return r.json()}).then(function(d){d.e.forEach(function(x){x.push(normD(x[2]))});cache[m.id]=d;return d})};
    var runS=function(){var my=++gen;var terms=normD(q.value.trim()).split(/\s+/).filter(Boolean);
      if(!terms.length){res.innerHTML="";st.textContent="खोजनेके लिये लिखें · Type to search.";return}
      var list=sel.value==="all"?meta:meta.filter(function(m){return m.id===sel.value});
      var hits=[],done=0,LIMIT=100;res.innerHTML="";
      var render=function(){st.textContent=(hits.length>=LIMIT?LIMIT+"+":hits.length)+" matches · searched "+done+"/"+list.length+" parva"+(list.length>1?"s":"")+(done<list.length?" …":"");
        res.innerHTML=hits.slice(0,LIMIT).map(function(h){return '<li><a href="'+h.d+'/'+h.x[0]+(h.x[1]?"#"+h.x[1]:"")+'">'+esc(h.n)+' · अध्याय '+esc(h.x[0].replace(/\.html$/,"").replace(/^0+/,""))+(h.x[1]?" · "+esc(h.x[1].replace(/^s/,"श्लोक ")):"")+'</a><p>'+snippet(h.x[2],terms)+'</p></li>'}).join("")};
      (function next(i){if(my!==gen)return;if(i>=list.length||hits.length>=LIMIT){done=Math.max(done,i);render();if(!hits.length&&i>=list.length)st.textContent="No matches · कुछ नहीं मिला";return}
        getShard(list[i]).then(function(d){if(my!==gen)return;for(var j=0;j<d.e.length&&hits.length<LIMIT;j++){var x=d.e[j],ok=true;for(var t=0;t<terms.length;t++){if(x[3].indexOf(terms[t])<0){ok=false;break}}if(ok)hits.push({d:d.dir,n:d.name,x:x})}
          done=i+1;render();next(i+1)}).catch(function(){st.textContent="Could not load the search index (serve the site over http)."})})(0)};
    var params=new URLSearchParams(location.search);if(params.get("p")&&meta.some(function(m){return m.id===params.get("p")}))sel.value=params.get("p");
    var tm2;q.addEventListener("input",function(){clearTimeout(tm2);tm2=setTimeout(function(){runS();history.replaceState(null,"","?q="+encodeURIComponent(q.value)+"&p="+sel.value)},250)});
    sel.addEventListener("change",function(){runS()});
    if(params.get("q"))q.value=params.get("q");runS();
  }
  else if(q&&res){
    var run=function(){var v=norm(q.value.trim());var terms=v.split(/\s+/).filter(Boolean);
      if(!terms.length){res.innerHTML="";st.textContent="Type to search.";return}
      st.textContent="Searching…";
      load().then(function(d){var hits=[];for(var i=0;i<d.length&&hits.length<400;i++){var x=d[i],ok=true;for(var j=0;j<terms.length;j++){if(x.n.indexOf(terms[j])<0){ok=false;break}}if(ok)hits.push(x)}
        hits.sort(function(a,b){return (b.k==="tag")-(a.k==="tag")||(b.k==="verse")-(a.k==="verse")});
        st.textContent=hits.length?("Showing "+Math.min(50,hits.length)+" of "+hits.length+(hits.length>=400?"+":"")+" matches"):"No matches.";
        res.innerHTML=hits.slice(0,50).map(function(x){return '<li><a href="'+secRoot+x.u+'">'+esc(x.h||x.id)+'</a><span class="where">'+esc(x.c||"")+'</span><p>'+snippet(x.t,terms)+'</p></li>'}).join("")})
      .catch(function(){st.textContent="Could not load the search index (open the site through a web server, not file://)."})};
    var tmr;q.addEventListener("input",function(){clearTimeout(tmr);tmr=setTimeout(function(){run();history.replaceState(null,"","?q="+encodeURIComponent(q.value))},180)});
    var p=new URLSearchParams(location.search).get("q");if(p){q.value=p}run();
  }
})();
