export function connect(onState,onStatus=()=>{}) {
 let socket, timer, retry=500, stopped=false;
 const open=()=>{
  socket=new WebSocket(`${location.protocol==='https:'?'wss':'ws'}://${location.host}/ws`);
  socket.onopen=()=>{retry=500;onStatus(true)};
  socket.onmessage=e=>{const s=JSON.parse(e.data);if(s.type==='state')onState(s)};
  socket.onerror=()=>socket.close();
  socket.onclose=()=>{onStatus(false);if(!stopped){timer=setTimeout(open,retry);retry=Math.min(10000,retry*2)}};
 };open();return ()=>{stopped=true;clearTimeout(timer);socket.close()};
}
export async function send(event){
 const r=await fetch('/api/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(event)});
 const data=await r.json();if(!r.ok)throw Error(typeof data.detail==='string'?data.detail:'Alanları kontrol edin');return data;
}
