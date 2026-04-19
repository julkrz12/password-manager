let token = null;

function $(id){return document.getElementById(id)}

function setSession(t, ttl){
  token = t;
  if(t){ $('sessionInfo').textContent = `Sesja aktywna (${ttl} min TTL)`; }
  else { $('sessionInfo').textContent = 'Brak sesji'; }
}

async function post(url, body){
  const r = await fetch(url, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  const data = await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(data.detail || r.statusText);
  return data;
}

async function put(url, body){
  const r = await fetch(url, {
    method:'PUT',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  const data = await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(data.detail || r.statusText);
  return data;
}

async function get(url){
  const r = await fetch(url);
  const data = await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(data.detail || r.statusText);
  return data;
}

function show(outId, obj){
  $(outId).textContent = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
}

$('btnRegister').onclick = async () => {
  try{
    const res = await post('/auth/register', {username: $('regUser').value.trim(), master_password: $('regPass').value});
    setSession(res.token, res.ttl_minutes);
    show('entryOut','Zarejestrowano i zalogowano');
    await refreshEntries();
  }catch(e){show('entryOut', e.message)}
};

$('btnLogin').onclick = async () => {
  try{
    const res = await post('/auth/login', {username: $('logUser').value.trim(), master_password: $('logPass').value});
    setSession(res.token, res.ttl_minutes);
    show('entryOut','Zalogowano');
    await refreshEntries();
  }catch(e){show('entryOut', e.message)}
};

$('btnLogout').onclick = async () => {
  setSession(null, 0);
  $('entries').innerHTML='';
  show('entryOut','Wylogowano');
};

$('btnStrength').onclick = async () => {
  try{
    const res = await post('/tools/strength', {password: $('toolPassword').value});
    show('strengthOut', res);
  }catch(e){show('strengthOut', e.message)}
};

$('btnGen').onclick = async () => {
  try{
    const res = await post('/tools/generate', {length: parseInt($('genLen').value || '16',10)});
    show('genOut', res);
  }catch(e){show('genOut', e.message)}
};

$('btnLeak').onclick = async () => {
  try{
    const res = await post('/tools/leak', {password: $('toolPassword').value});
    show('leakOut', res);
  }catch(e){show('leakOut', e.message)}
};

$('btnAdd').onclick = async () => {
  if(!token){ show('entryOut','Najpierw zaloguj się'); return; }
  try{
    const res = await fetch(`/vault/entries?token=${token}`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        title: $('eTitle').value,
        url: $('eUrl').value,
        account_username: $('eUser').value,
        password: $('ePass').value,
        notes: $('eNotes').value
      })
    });
    const data = await res.json().catch(()=>({}));
    if(!res.ok) throw new Error(data.detail || res.statusText);
    show('entryOut', {ok:true, created:data});
    $('ePass').value='';
    await refreshEntries();
  }catch(e){show('entryOut', e.message)}
};

$('btnRefresh').onclick = refreshEntries;

async function refreshEntries(){
  if(!token) return;
  try{
    const items = await get(`/vault/entries?token=${token}`);
    const ul = $('entries');
    ul.innerHTML='';
    items.forEach(it => {
      const li = document.createElement('li');
      li.innerHTML = `<span><b>${escapeHtml(it.title)}</b><br><span class="muted">${escapeHtml(it.url||'')}</span></span>`;
      const btn = document.createElement('button');
      btn.textContent='Pokaż';
      btn.onclick = () => showEntry(it.id);
      li.appendChild(btn);
      ul.appendChild(li);
    });
  }catch(e){show('entryOut', e.message)}
}

async function showEntry(id){
  if(!token) return;
  try{
    const e = await get(`/vault/entries/${id}?token=${token}`);
    show('entryOut', e);
  }catch(err){show('entryOut', err.message)}
}

$('btnDup').onclick = async () => {
  if(!token){ show('dupOut','Najpierw zaloguj się'); return; }
  try{
    const res = await get(`/vault/duplicates?token=${token}`);
    show('dupOut', res);
  }catch(e){show('dupOut', e.message)}
};

function escapeHtml(s){
  return (s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}
