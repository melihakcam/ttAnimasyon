import json, unittest, time
from pathlib import Path
from types import SimpleNamespace as NS
from engine import Engine
from tiktok_listener import gift_payload

class Rules(unittest.TestCase):
    def setUp(self):
        self.e=Engine(json.loads((Path(__file__).parents[1]/'config.json').read_text(encoding='utf-8')))
    def event(self,**kwargs):
        d=dict(type='comment',user_id='u',name='User',text='merhaba',count=1,gift='Rose')
        d.update(kwargs);self.e.apply(d)
    def test_join_and_costume(self):
        self.event(text='kız');self.assertTrue(self.e.users['u']['joined']);self.assertEqual(self.e.users['u']['costume'],'kız')
        self.event(text='erkek');self.assertEqual(self.e.users['u']['costume'],'erkek')
    def test_likes_threshold_per_user(self):
        self.event(type='like',count=299);self.assertFalse(self.e.users['u']['joined'])
        self.event(type='like',count=1);self.assertTrue(self.e.users['u']['joined'])
    def test_gift_dedup(self):
        self.event(type='gift',count=5,event_id='one');self.event(type='gift',count=5,event_id='one')
        self.assertEqual(self.e.users['u']['points'],5)
    def test_drummers_exclusive(self):
        self.event(type='gift',gift='Drum');self.event(type='gift',gift='Drum',user_id='v')
        self.assertEqual(sum(u['role']=='drummer' for u in self.e.users.values()),1)
    def test_speed_expiry_and_scene(self):
        self.event(type='gift',gift='Heart Me');self.assertGreater(self.e.speed_until,time.time())
        self.event(type='control',text='orbit');self.assertEqual(self.e.scene,'orbit')
    def test_capacity(self):
        self.e.config['max_users']=1;self.event()
        with self.assertRaises(ValueError): self.event(user_id='v')
    def test_streak_final_only(self):
        g=NS(gift=NS(streakable=True,name='Rose',id=5655),streaking=True,repeat_count=3,user=NS(unique_id='u',id=1,nickname='User'),order_id='abc')
        self.assertIsNone(gift_payload(g));g.streaking=False
        payload=gift_payload(g);self.assertEqual(payload['count'],3);self.assertEqual(payload['event_id'],'tiktok-gift:abc')
    def test_demo_at_capacity_is_bounded(self):
        self.e.config['max_users']=1
        self.event()
        self.event(type='control',text='demo')
        self.assertEqual(len(self.e.users),1)
    def test_reset_preserves_delivery_dedup(self):
        self.event(type='gift',event_id='one');self.event(type='control',text='reset')
        self.event(type='gift',event_id='one');self.assertEqual(self.e.users,{})
if __name__=='__main__': unittest.main()

class InstalledTikTokCompatibility(unittest.TestCase):
    def test_real_v7_gift_events(self):
        try:
            from TikTokLive.events import GiftEvent
        except ImportError:
            self.skipTest('Optional TikTokLive not installed')
        raw={'gift':{'id':5655,'name':'Rose','type':1},'user':{'id':1,'displayId':'qa','nickname':'QA'},'repeatCount':4,'repeatEnd':0,'orderId':'real-event'}
        self.assertIsNone(gift_payload(GiftEvent.from_dict(raw)))
        raw['repeatEnd']=1
        p=gift_payload(GiftEvent.from_dict(raw))
        self.assertEqual(p['count'],4)
        self.assertEqual(p['user_id'],'qa')
        self.assertEqual(p['event_id'],'tiktok-gift:real-event')
