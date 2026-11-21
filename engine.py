"""Transport-independent scene state. Add gift mappings in config.json."""
import time, random
from collections import OrderedDict

class Engine:
    def __init__(self, config):
        self.config = config
        self.seen = OrderedDict()
        self.reset()

    def reset(self):
        self.users = {}
        self.events = []
        self.speed_until = 0
        self.effect_until = 0
        self.scene = 'halay'
        self.layout = 'circle'
        self.theme = 'night'
        self.quality = 'balanced'
        self.music = 'halay'
        self.volume = 45
        self.ring_capacity = self.config.get('ring_capacity',24)
        self.source = 'Test modu'
        self.revision = getattr(self, 'revision', 0) + 1

    def user(self, uid, name):
        if uid not in self.users:
            if len(self.users) >= self.config['max_users']:
                raise ValueError('Sahne kapasitesi dolu; katılımcı silin veya sahneyi sıfırlayın.')
            self.users[uid] = dict(id=uid, name=name, points=0, likes=0, joined=False,
                                   costume='kız', avatar='', role='', bubble='', bubble_until=0,
                                   color=random.choice(['#7a1e2c','#842738','#5a1b2a','#1f1a1f','#24222d','#154e40','#172d50']))
        self.users[uid]['name'] = name
        return self.users[uid]

    def apply(self, e):
        eid = e.get('event_id')
        if eid and eid in self.seen:
            return False
        kind = e['type']
        now = time.time()
        if kind == 'control':
            action = e['text']
            if action == 'reset':
                old_scene,old_capacity,old_source=self.scene,self.ring_capacity,self.source
                old_layout,old_theme,old_quality=self.layout,self.theme,self.quality
                old_music,old_volume=self.music,self.volume
                self.reset()
                self.scene,self.ring_capacity,self.source=old_scene,old_capacity,old_source
                self.layout,self.theme,self.quality=old_layout,old_theme,old_quality
                self.music,self.volume=old_music,old_volume
            elif action == 'demo':
                for i, name in enumerate(['Melih','Zeynep','Efe','Elif','Baran','Dilan','Deniz','Yağmur','Can','Sinem','Mert','Bahar','Ali','Ceren','Umut','Nehir','Aslı','Emre']):
                    uid='demo'+str(i)
                    if uid not in self.users and len(self.users)>=self.config['max_users']: break
                    u = self.user(uid,name)
                    u.update(joined=True, costume='erkek' if i%3==0 else 'kız', points=(18-i)*3)
                if 'demo0' in self.users: self.assign_role(self.users['demo0'],'drummer')
                if 'demo1' in self.users: self.assign_role(self.users['demo1'],'zurnaci')
            elif action in ('halay','orbit'):
                self.scene=action
            elif action == 'speed':
                self.speed_until = now+20
            elif action == 'remove':
                self.users.pop(e['user_id'],None)
            else:
                raise ValueError('Bilinmeyen kontrol komutu')
        elif kind == 'connection':
            self.source = e['text']
        else:
            u = self.user(e['user_id'],e['name'])
            if e.get('avatar'):
                u['avatar']=e['avatar']
            if kind == 'comment':
                text = e['text'].strip()
                command = text.lower().replace('ı','i')
                # The reference visibly invites comments to join.
                u['joined'] = True
                if command in ('kiz','qiz','erkek','oğlan','oglan'):
                    u['costume'] = 'kız' if command in ('kiz','qiz') else 'erkek'
                elif command in ('oyuncak','ahşap','köşeli','ayi','tilki','kedi','tavşan','koyun','penguen'):
                    u['costume']=text.lower()
                u.update(bubble=text, bubble_until=now+6)
            elif kind == 'like':
                u['likes'] += e['count']
                if u['likes'] >= self.config['like_threshold']:
                    u['joined']=True
            elif kind == 'gift':
                rule = self.config['gift_ids'].get(str(e.get('gift_id',0))) or self.config['gift_rules'].get(e['gift'], {'action':'join','points':1})
                u['joined']=True
                u['points'] += rule['points']*e['count']
                action=rule['action']
                if action=='speed': self.speed_until=now+min(60,10+e['count']*2)
                if action=='confetti': self.effect_until=now+8
                if action=='drummer': self.assign_role(u,'drummer')
                if action=='zurna': self.assign_role(u,'zurnaci')
        self.admit()
        if eid:
            self.seen[eid]=True
            if len(self.seen)>4000: self.seen.popitem(last=False)
        self.revision+=1
        self.events.append(dict(type=kind,name=e.get('name','Sistem'),text=e.get('gift','') if kind=='gift' else e.get('text','') if kind in ('comment','control','connection') else 'Beğeni',count=e.get('count',1),at=now))
        self.events=self.events[-40:]
        return True

    def assign_role(self, user, role):
        # Nağaracı ve zurnacı tektir; yeni sahibi eskisinin yerini alır.
        for other in self.users.values():
            if other['role']==role: other['role']=''
        user['role']=role

    def admit(self):
        count=0
        # Nağaracı ve zurnacı sahnede görünmeli; halka doluysa sıradan önce alınırlar.
        for u in sorted(self.users.values(), key=lambda u: not u['role']):
            if not (u['joined'] or u.get('queued')): continue
            count+=1
            u['joined']=count<=self.ring_capacity
            u['queued']=not u['joined']

    def snapshot(self):
        return dict(type='state',revision=self.revision,server_time=time.time(),users=list(self.users.values()),
                    events=self.events,scene=self.scene,layout=self.layout,theme=self.theme,quality=self.quality,music=self.music,volume=self.volume,ring_capacity=self.ring_capacity,queued=sum(bool(u.get('queued')) for u in self.users.values()),speed_until=self.speed_until,effect_until=self.effect_until,
                    bpm=self.config['base_bpm'],source=self.source,like_threshold=self.config['like_threshold'],
                    gift_names=list(self.config['gift_rules']))
