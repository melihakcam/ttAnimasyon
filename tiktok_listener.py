"""Optional TikTok -> local HTTP -> WebSocket bridge. No account password needed."""
import asyncio, argparse, json, logging
from urllib.request import Request, urlopen
from urllib.error import URLError

log=logging.getLogger('tiktok-bridge')

def gift_payload(event):
    gift=event.gift
    if gift is None or event.user is None or (gift.streakable and event.streaking): return None
    u=event.user
    payload=dict(type='gift',user_id=str(u.unique_id or u.id),name=str(u.nickname or u.unique_id or 'Misafir')[:40],
                 gift=str(gift.name),gift_id=int(gift.id),count=max(1,int(event.repeat_count or 1)))
    # order_id identifies a delivery; don't guess an ID from user/gift/count (separate gifts may match).
    oid=getattr(event,'order_id',None)
    if oid: payload['event_id']='tiktok-gift:'+str(oid)
    return payload

class Bridge:
    def __init__(self): self.queue=asyncio.Queue(maxsize=1000)
    def put(self,payload):
        try: self.queue.put_nowait(payload)
        except asyncio.QueueFull: log.error('Olay kuyruğu dolu; olay alınamadı: %s',payload.get('type'))
    @staticmethod
    def post(payload):
        data=json.dumps(payload,ensure_ascii=False).encode()
        req=Request('http://127.0.0.1:8765/api/event',data=data,headers={'Content-Type':'application/json'})
        with urlopen(req,timeout=4) as res: return res.status
    async def worker(self):
        while True:
            payload=await self.queue.get()
            try:
                # Single delivery attempt prevents duplicate non-idempotent like/comment events.
                await asyncio.to_thread(self.post,payload)
            except (URLError,TimeoutError,OSError) as exc: log.error('Yerel sunucuya gönderilemedi: %s',exc)
            finally: self.queue.task_done()

async def main(username):
    try:
        from TikTokLive import TikTokLiveClient
        from TikTokLive.events import CommentEvent,GiftEvent,LikeEvent,ConnectEvent,DisconnectEvent
    except ImportError:
        raise SystemExit('Önce TIKTOK_KUR.cmd dosyasını çalıştırın.')
    bridge=Bridge()
    client=TikTokLiveClient(unique_id=username)
    def user_fields(event):
        u=event.user
        if u is None: return None
        return dict(user_id=str(u.unique_id or u.id),name=str(u.nickname or u.unique_id or 'Misafir')[:40])
    @client.on(ConnectEvent)
    async def connected(event):
        log.info('TikTok yayınına bağlandı: %s',username)
        bridge.put(dict(type='connection',text='TikTok bağlı: '+username))
    @client.on(DisconnectEvent)
    async def disconnected(event):
        bridge.put(dict(type='connection',text='TikTok bağlantısı kesildi'))
    @client.on(CommentEvent)
    async def comment(event):
        fields=user_fields(event)
        if fields: bridge.put(dict(type='comment',text=str(event.comment)[:250],**fields))
    @client.on(LikeEvent)
    async def like(event):
        fields=user_fields(event)
        if fields: bridge.put(dict(type='like',count=max(1,min(100000,int(event.count))),**fields))
    @client.on(GiftEvent)
    async def gift(event):
        payload=gift_payload(event)
        if payload: bridge.put(payload)
    task=asyncio.create_task(bridge.worker())
    delay=3
    try:
        while True:
            try:
                await client.connect()
                delay=3
            except Exception as exc:
                log.error('TikTok bağlantısı kurulamadı: %s',exc)
            bridge.put(dict(type='connection',text='TikTok yeniden bağlanıyor…'))
            await asyncio.sleep(delay)
            delay=min(60,delay*2)
    finally:
        task.cancel()
        await asyncio.gather(task,return_exceptions=True)

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    parser=argparse.ArgumentParser(description='TikTok canlı yayın olay köprüsü')
    parser.add_argument('username',help='Canlı yayın yapan hesabın @kullaniciadi')
    try: asyncio.run(main(parser.parse_args().username))
    except KeyboardInterrupt: pass
