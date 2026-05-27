let token = null;
let allEntries = [];
let currentEditEntryId = null;
let visiblePasswords = new Set();

function $(id){ return document.getElementById(id); }

function escapeHtml(s){
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;'
  }[c]));
}

function setSession(t, ttl){
  token = t;
  $('sessionInfo').textContent = t ? `Sesja aktywna (${ttl} min)` : 'Brak sesji';
  $('sessionInfo').classList.toggle('active', Boolean(t));
}

async function request(url, options = {}){
  const r = await fetch(url, options);
  const data = await r.json().catch(() => ({}));
  if(!r.ok) throw new Error(data.detail || r.statusText || 'Wystąpił błąd');
  return data;
}

function post(url, body){
  return request(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
}

function put(url, body){
  return request(url, {
    method: 'PUT',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
}

function del(url){
  return request(url, { method: 'DELETE' });
}

function get(url){
  return request(url);
}

function toast(message, type = 'success'){
  const root = $('toastRoot');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = message;
  root.appendChild(el);
  setTimeout(() => el.classList.add('hide'), 2600);
  setTimeout(() => el.remove(), 3200);
}

function formatCount(n){
  const num = Number(n || 0);
  if(num >= 1000000) return `+${Math.round(num / 1000000)}M`;
  if(num >= 1000) return `+${Math.round(num / 1000)}k`;
  return String(num);
}

function validateEntryForm(){
  let ok = true;
  const title = $('eTitle').value.trim();
  const pass = $('ePass').value;

  $('titleError').textContent = '';
  $('passError').textContent = '';

  if(!title){
    $('titleError').textContent = 'Tytuł jest wymagany.';
    ok = false;
  }
  if(!pass){
    $('passError').textContent = 'Hasło jest wymagane.';
    ok = false;
  }
  return ok;
}

function validateEditForm(){
  $('editPassError').textContent = '';
  if(!$('editPass').value){
    $('editPassError').textContent = 'Hasło nie może być puste.';
    return false;
  }
  return true;
}

function resetEntryForm(){
  $('eTitle').value = '';
  $('eUrl').value = '';
  $('eUser').value = '';
  $('ePass').value = '';
  $('eNotes').value = '';
}

function showStrength(res){
  const score = Number(res.score ?? 0);
  const label = res.label || '—';
  const length = res.length ?? '—';
  const entropy = res.entropy_bits ?? '—';
  const issues = Array.isArray(res.issues) ? res.issues : [];

  $('strengthLabel').textContent = label;
  $('strengthScore').textContent = `${score}%`;
  $('strengthLength').textContent = length;
  $('strengthEntropy').textContent = entropy === '—' ? '—' : `${entropy} bit`;

  $('strengthLabel').classList.remove('placeholder-text');
  $('strengthLength').classList.remove('placeholder-text');
  $('strengthEntropy').classList.remove('placeholder-text');
  $('strengthScore').classList.remove('muted-badge');

  const fill = $('strengthBarFill');
  fill.style.width = `${Math.max(0, Math.min(100, score))}%`;
  fill.className = '';
  if(score < 40) fill.classList.add('weak');
  else if(score < 70) fill.classList.add('medium');
  else fill.classList.add('strong');

  $('strengthIssues').innerHTML = issues.length
    ? issues.slice(0, 4).map(i => `<div>⚠️ ${escapeHtml(i)}</div>`).join('')
    : '<div class="good">✅ Brak ważnych problemów</div>';
}

function showGeneratedPassword(res){
  const password = res.password || res.generated_password || '';
  $('generatedPassword').textContent = password || '—';
  $('generatedPassword').classList.toggle('placeholder-text', !password);
  $('copyGeneratedBtn').disabled = !password;
}

function showLeak(res){
  const online = res.online || {};
  const offline = res.offline || {};
  const isPwned = Boolean(online.pwned || offline.pwned);
  const count = online.count || offline.count || 0;

  $('leakStatus').textContent = isPwned ? 'Hasło znalezione w wyciekach' : 'Nie znaleziono w wyciekach';
  $('leakStatus').className = isPwned ? 'danger-text' : 'safe-text';
  $('leakCount').textContent = isPwned ? `Wystąpienia: ${formatCount(count)}` : 'Wygląda bezpiecznie w tym sprawdzeniu';
}

function showDuplicates(res){
  const groups = Array.isArray(res.duplicates) ? res.duplicates : [];
  if(!groups.length){
    $('dupStatus').textContent = 'Brak duplikatów';
    $('dupStatus').className = 'safe-text';
    $('dupList').innerHTML = 'Nie znaleziono wpisów z tym samym hasłem.';
    return;
  }

  $('dupStatus').textContent = `Znaleziono ${groups.length} grup`;
  $('dupStatus').className = 'danger-text';
  $('dupList').innerHTML = groups.map((group, idx) => `
    <div class="duplicate-group">
      <strong>Grupa ${idx + 1}</strong>
      ${group.map(i => `<span>${escapeHtml(i.title)} ${i.url ? `— ${escapeHtml(i.url)}` : ''}</span>`).join('')}
    </div>
  `).join('');
}

function renderEntries(){
  const q = $('entrySearch').value.trim().toLowerCase();
  const list = $('entries');
  const filtered = allEntries.filter(it =>
    String(it.title || '').toLowerCase().includes(q) ||
    String(it.url || '').toLowerCase().includes(q)
  );

  $('entriesCount').textContent = `${allEntries.length} ${allEntries.length === 1 ? 'wpis' : 'wpisów'}`;
  list.innerHTML = '';
  $('emptyState').classList.toggle('hidden', filtered.length > 0);

  filtered.forEach(it => {
    const li = document.createElement('li');
    li.className = 'entry-item';
    li.innerHTML = `
      <div class="entry-main">
        <b>${escapeHtml(it.title)}</b>
        <span>${escapeHtml(it.url || 'Brak URL')}</span>
      </div>
      <div class="entry-actions">
        <button class="secondary" data-action="copy" data-id="${it.id}">Skopiuj</button>
        <button data-action="show" data-id="${it.id}">Pokaż</button>
        <button class="secondary" data-action="edit" data-id="${it.id}">Edytuj</button>
      </div>
    `;
    list.appendChild(li);
  });
}

async function refreshEntries(){
  if(!token){
    allEntries = [];
    renderEntries();
    return;
  }
  try{
    allEntries = await get(`/vault/entries?token=${encodeURIComponent(token)}`);
    renderEntries();
  }catch(e){ toast(e.message, 'error'); }
}

async function getFullEntry(id){
  return get(`/vault/entries/${id}?token=${encodeURIComponent(token)}`);
}

async function copyEntryPassword(id){
  try{
    const e = await getFullEntry(id);
    await navigator.clipboard.writeText(e.password || '');
    toast('Hasło skopiowane ✅');
  }catch(e){ toast(e.message, 'error'); }
}

async function showEntryPassword(id){
  try{
    const e = await getFullEntry(id);
    await navigator.clipboard.writeText(e.password || '');
    toast(`Hasło dla „${e.title}” skopiowane ✅`);
  }catch(e){ toast(e.message, 'error'); }
}

async function openEditModal(id){
  try{
    const e = await getFullEntry(id);
    currentEditEntryId = e.id;
    $('modalTitle').textContent = `Edytuj: ${e.title}`;
    $('editUrl').value = e.url || '';
    $('editUser').value = e.account_username || '';
    $('editPass').value = e.password || '';
    $('editNotes').value = e.notes || '';
    $('editPassError').textContent = '';
    $('editModal').classList.remove('hidden');
  }catch(e){ toast(e.message, 'error'); }
}

function closeEditModal(){
  $('editModal').classList.add('hidden');
  currentEditEntryId = null;
}

async function saveEdit(){
  if(!token || !currentEditEntryId) return;
  if(!validateEditForm()) return;

  try{
    await put(`/vault/entries/${currentEditEntryId}?token=${encodeURIComponent(token)}`, {
      url: $('editUrl').value.trim(),
      account_username: $('editUser').value.trim(),
      password: $('editPass').value,
      notes: $('editNotes').value
    });
    toast('Wpis zaktualizowany ✅');
    closeEditModal();
    await refreshEntries();
  }catch(e){ toast(e.message, 'error'); }
}

async function deleteEntry(){
  if(!token || !currentEditEntryId) return;
  if(!confirm('Na pewno usunąć ten wpis?')) return;

  try{
    await del(`/vault/entries/${currentEditEntryId}?token=${encodeURIComponent(token)}`);
    toast('Wpis usunięty ✅');
    closeEditModal();
    await refreshEntries();
  }catch(e){ toast(e.message, 'error'); }
}

$('btnRegister').onclick = async () => {
  try{
    const username = $('regUser').value.trim();
    const password = $('regPass').value;
    if(username.length < 3) return toast('Login musi mieć minimum 3 znaki.', 'error');
    if(password.length < 8) return toast('Hasło główne musi mieć minimum 8 znaków.', 'error');

    const res = await post('/auth/register', { username, master_password: password });
    setSession(res.token, res.ttl_minutes);
    toast('Zarejestrowano i zalogowano ✅');
    await refreshEntries();
  }catch(e){ toast(e.message, 'error'); }
};

$('btnLogin').onclick = async () => {
  try{
    const res = await post('/auth/login', {
      username: $('logUser').value.trim(),
      master_password: $('logPass').value
    });
    setSession(res.token, res.ttl_minutes);
    toast('Zalogowano ✅');
    await refreshEntries();
  }catch(e){ toast(e.message, 'error'); }
};

$('btnLogout').onclick = async () => {
  setSession(null, 0);
  allEntries = [];
  visiblePasswords.clear();
  renderEntries();
  toast('Wylogowano');
};

$('btnToggleToolPassword').onclick = () => {
  const input = $('toolPassword');
  const visible = input.type === 'text';
  input.type = visible ? 'password' : 'text';
  $('btnToggleToolPassword').textContent = visible ? 'Pokaż' : 'Ukryj';
};

$('btnStrength').onclick = async () => {
  try{
    const password = $('toolPassword').value;
    if(!password) return toast('Wpisz hasło do analizy.', 'error');
    const res = await post('/tools/strength', { password, use_hibp: false });
    showStrength(res);
  }catch(e){ toast(e.message, 'error'); }
};

$('btnGen').onclick = async () => {
  try{
    const length = parseInt($('genLen').value || '16', 10);
    if(length < 8 || length > 64) return toast('Długość musi być między 8 a 64.', 'error');
    const res = await post('/tools/generate', { length });
    showGeneratedPassword(res);
    toast('Wygenerowano hasło ✅');
  }catch(e){ toast(e.message, 'error'); }
};

$('copyGeneratedBtn').onclick = async () => {
  const password = $('generatedPassword').textContent;
  if(!password || password === '—') return;
  await navigator.clipboard.writeText(password);
  toast('Hasło skopiowane ✅');
};

$('btnLeak').onclick = async () => {
  try{
    const password = $('toolPassword').value;
    if(!password) return toast('Wpisz hasło do sprawdzenia.', 'error');
    const res = await post('/tools/leak', {
      password,
      use_hibp: $('useHibpCheckbox').checked
    });
    showLeak(res);
  }catch(e){ toast(e.message, 'error'); }
};

$('entryForm').onsubmit = async (ev) => {
  ev.preventDefault();
  if(!token) return toast('Najpierw się zaloguj.', 'error');
  if(!validateEntryForm()) return;

  try{
    await post(`/vault/entries?token=${encodeURIComponent(token)}`, {
      title: $('eTitle').value.trim(),
      url: $('eUrl').value.trim(),
      account_username: $('eUser').value.trim(),
      password: $('ePass').value,
      notes: $('eNotes').value
    });
    resetEntryForm();
    toast('Wpis dodany do sejfu ✅');
    await refreshEntries();
  }catch(e){ toast(e.message, 'error'); }
};

$('btnRefresh').onclick = refreshEntries;
$('entrySearch').oninput = renderEntries;

$('entries').onclick = async (ev) => {
  const btn = ev.target.closest('button');
  if(!btn) return;
  const id = Number(btn.dataset.id);
  const action = btn.dataset.action;
  if(action === 'copy') await copyEntryPassword(id);
  if(action === 'show') await showEntryPassword(id);
  if(action === 'edit') await openEditModal(id);
};

$('btnDup').onclick = async () => {
  if(!token) return toast('Najpierw się zaloguj.', 'error');
  try{
    const res = await get(`/vault/duplicates?token=${encodeURIComponent(token)}`);
    showDuplicates(res);
  }catch(e){ toast(e.message, 'error'); }
};

$('btnCloseModal').onclick = closeEditModal;
$('editModal').onclick = (ev) => {
  if(ev.target.id === 'editModal') closeEditModal();
};
$('btnSaveEdit').onclick = saveEdit;
$('btnDeleteEntry').onclick = deleteEntry;

document.addEventListener('keydown', ev => {
  if(ev.key === 'Escape') closeEditModal();
});

renderEntries();
