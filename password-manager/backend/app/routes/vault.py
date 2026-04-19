from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import get_db
from ..models import Entry
from ..schemas import EntryCreateRequest, EntryUpdateRequest, EntryListItem, EntryDetail
from ..core.session_store import get_session
from ..core.crypto import encrypt_secret, decrypt_secret, password_fingerprint

router = APIRouter(prefix='/vault', tags=['vault'])


def _require_session(token: str):
    s = get_session(token)
    if not s:
        raise HTTPException(status_code=401, detail='Brak lub wygasła sesja')
    return s


@router.get('/entries', response_model=list[EntryListItem])
def list_entries(token: str, db: Session = Depends(get_db)):
    s = _require_session(token)
    q = db.query(Entry).filter(Entry.user_id == s.user_id).order_by(Entry.updated_at.desc())
    return [EntryListItem(id=e.id, title=e.title, url=e.url) for e in q.all()]


@router.post('/entries', response_model=EntryListItem)
def create_entry(payload: EntryCreateRequest, token: str, db: Session = Depends(get_db)):
    s = _require_session(token)

    secret = {
        'account_username': payload.account_username,
        'password': payload.password,
        'notes': payload.notes,
    }
    ct, nonce = encrypt_secret(s.key, secret)
    fp = password_fingerprint(s.key, payload.password)

    e = Entry(
        user_id=s.user_id,
        title=payload.title,
        url=payload.url,
        secret_ciphertext=ct,
        secret_nonce=nonce,
        pw_fingerprint=fp,
    )
    db.add(e)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail='Wpis o takim tytule już istnieje')

    db.refresh(e)
    return EntryListItem(id=e.id, title=e.title, url=e.url)


@router.get('/entries/{entry_id}', response_model=EntryDetail)
def get_entry(entry_id: int, token: str, db: Session = Depends(get_db)):
    s = _require_session(token)
    e = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == s.user_id).first()
    if not e:
        raise HTTPException(status_code=404, detail='Nie znaleziono')

    secret = decrypt_secret(s.key, e.secret_ciphertext, e.secret_nonce)
    return EntryDetail(
        id=e.id,
        title=e.title,
        url=e.url,
        account_username=secret.get('account_username',''),
        password=secret.get('password',''),
        notes=secret.get('notes',''),
    )


@router.put('/entries/{entry_id}', response_model=EntryListItem)
def update_entry(entry_id: int, payload: EntryUpdateRequest, token: str, db: Session = Depends(get_db)):
    from datetime import datetime
    s = _require_session(token)
    e = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == s.user_id).first()
    if not e:
        raise HTTPException(status_code=404, detail='Nie znaleziono')

    # zdejmij tajne dane, zaktualizuj, ponownie zaszyfruj
    secret = decrypt_secret(s.key, e.secret_ciphertext, e.secret_nonce)

    if payload.url is not None:
        e.url = payload.url

    if payload.account_username is not None:
        secret['account_username'] = payload.account_username

    if payload.password is not None:
        secret['password'] = payload.password
        e.pw_fingerprint = password_fingerprint(s.key, payload.password)

    if payload.notes is not None:
        secret['notes'] = payload.notes

    ct, nonce = encrypt_secret(s.key, secret)
    e.secret_ciphertext = ct
    e.secret_nonce = nonce
    e.updated_at = datetime.utcnow()

    db.add(e)
    db.commit()
    db.refresh(e)
    return EntryListItem(id=e.id, title=e.title, url=e.url)


@router.delete('/entries/{entry_id}')
def delete_entry(entry_id: int, token: str, db: Session = Depends(get_db)):
    s = _require_session(token)
    e = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == s.user_id).first()
    if not e:
        raise HTTPException(status_code=404, detail='Nie znaleziono')
    db.delete(e)
    db.commit()
    return {'ok': True}


@router.get('/duplicates')
def find_duplicates(token: str, db: Session = Depends(get_db)):
    s = _require_session(token)
    entries = db.query(Entry).filter(Entry.user_id == s.user_id).all()
    # map fingerprint -> list titles
    mp = {}
    for e in entries:
        mp.setdefault(e.pw_fingerprint, []).append({'id': e.id, 'title': e.title, 'url': e.url})
    dups = [v for v in mp.values() if len(v) > 1]
    return {'duplicates': dups}
