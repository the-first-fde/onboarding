import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import demo from './demo-event.json';
import './style.css';
type Case = {id:string;candidate_id:string;employee_id:string;execution_status:string;tasks:{id:string;status:string;due_on:string}[]};
function App(){
  const [token,setToken]=useState('');
  const [cases,setCases]=useState<Case[]>([]);
  const [message,setMessage]=useState('로컬 demo 토큰을 입력하고 조회하세요.');
  const [busy,setBusy]=useState(false);
  async function request(path:string,body?:unknown){
    const res=await fetch('/api/'+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},...(body!==undefined?{body:JSON.stringify(body)}:{})});
    if(!res.ok) throw new Error(`요청 실패 (${res.status}). 토큰과 API 상태를 확인하세요.`);
    return res.json();
  }
  async function action(kind:'load'|'approve'|'worker'){
    setBusy(true);
    try{
      if(kind==='approve') await request('hire-confirmations',demo);
      if(kind==='worker') await request('mock-worker/tick',{});
      setCases(await request('cases'));
      setMessage(kind==='approve'?'합성 이벤트를 승인했습니다. 동일 이벤트 재승인은 중복 생성하지 않습니다.':kind==='worker'?'Mock 처리 결과를 갱신했습니다.':'조회했습니다.');
    }catch(e){setMessage(e instanceof Error?e.message:'요청 실패');}finally{setBusy(false);}
  }
  return <main className="mx-auto max-w-6xl px-6 py-12">
    <header className="flex flex-wrap items-center justify-between gap-4 border-b border-emerald-900/20 pb-7"><div><p className="text-xs tracking-[.22em] uppercase">Independent FDE Project / 01</p><h1 className="mt-3 text-4xl font-semibold">HR Operations</h1></div><span className="rounded-full bg-amber-100 px-4 py-2 text-sm">합성 데이터 · Mock 환경</span></header>
    <section className="py-10"><p className="text-sm text-emerald-800">채용 → 입사확정 → 온보딩</p><h2 className="mt-3 text-3xl">입사 준비를 한 흐름으로</h2><p className="mt-4 max-w-2xl text-slate-600">합격 통보와 입사 의사 확정을 구분합니다. HR이 승인한 입사확정만 온보딩을 만들며, 준비 요청은 이 화면에서 모의 처리합니다.</p></section>
    <section aria-label="Demo 승인" className="rounded-2xl bg-white p-6 shadow-sm"><label htmlFor="token" className="block text-sm font-medium">로컬 Demo HR 토큰</label><div className="mt-3 flex flex-wrap gap-3"><input id="token" type="password" value={token} onChange={e=>setToken(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2" autoComplete="off"/><button disabled={busy} onClick={()=>action('load')} className="rounded-lg border px-4 py-2">케이스 조회</button><button disabled={busy} onClick={()=>action('approve')} className="rounded-lg bg-emerald-900 px-4 py-2 text-white">합성 입사확정 승인</button><button disabled={busy} onClick={()=>action('worker')} className="rounded-lg border px-4 py-2">Mock 준비 요청 처리</button></div><p className="mt-4 text-sm text-slate-600" role="status" aria-live="polite">{message}</p><p className="mt-2 text-xs text-slate-500">실제 인증·메일 발송·전체 56개 업무·에이전트 분석은 아직 제공하지 않습니다.</p></section>
    <section className="mt-8 grid gap-5" aria-label="온보딩 케이스">{cases.length===0?<p className="py-10 text-slate-500">표시할 케이스가 없습니다. 승인 또는 조회 후 여기에 나타납니다.</p>:cases.map(c=><article key={c.id} className="rounded-2xl bg-white p-6"><div className="flex flex-wrap justify-between gap-3"><h3 className="text-xl font-medium">{c.candidate_id} → {c.employee_id}</h3><span className="text-sm">모의 실행: {c.execution_status}</span></div><ul className="mt-5 divide-y divide-slate-100">{c.tasks.map(t=><li key={t.id} className="flex flex-wrap justify-between gap-3 py-3"><span>{t.id} · {t.status}</span><span className="text-sm text-slate-500">기한 {t.due_on}</span></li>)}</ul></article>)}</section>
    <footer className="mt-12 border-t border-emerald-900/20 pt-5 text-xs text-slate-500">G0 명세 초안 / G1–G2 초기 수직 흐름 · 실제 업무 상태와 모델 분석을 표시하지 않습니다.</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<App/>);
