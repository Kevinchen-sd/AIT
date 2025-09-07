import React, { useEffect, useState } from "react";
import { KeepReplaceItem } from "../types";
import { InsightBadge } from "./InsightBadge";
import { Sparkline } from "./Sparkline";

export const InsightCard: React.FC<{ item: KeepReplaceItem }> = ({ item }) => {
  const m = item.metrics;
  const [spark, setSpark] = useState<number[] | null>(null);
  useEffect(() => {
    const d = new Date(); d.setMonth(d.getMonth() - 6);
    const start = d.toISOString().slice(0,10);
    fetch(`/v1/md/bars?symbol=${encodeURIComponent(item.symbol)}&start=${start}&adjust=CASHDIVIDENDS`)
      .then(async r => { if (!r.ok) throw new Error(await r.text()); return r.json(); })
      .then(data => setSpark((data.bars as any[]).map(b => b.c)))
      .catch(() => setSpark(null));
  }, [item.symbol]);
  const pct = (x:number)=> (x*100).toFixed(1)+"%";
  return (
    <div style={{border:"1px solid #e5e7eb", borderRadius:8, padding:12, background:"#fff"}}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:8}}>
        <h3 style={{margin:0,fontSize:18}}>{item.symbol}</h3>
        <InsightBadge action={item.action}/>
      </div>
      <div style={{display:"flex", gap:12, alignItems:"center", marginBottom:12}}>
        {spark ? <Sparkline data={spark}/> : <div style={{fontSize:12,color:"#9ca3af"}}>loading…</div>}
        <div style={{fontSize:12,color:"#6b7280"}}>as of {item.as_of}</div>
      </div>
      <div style={{display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:8, fontSize:13}}>
        <div style={cell()}>Trend: <b>{m.trend_ok ? "OK" : "Broken"}</b></div>
        <div style={cell()}>3M: <b>{pct(m.r3m)}</b></div>
        <div style={cell()}>6M: <b>{pct(m.r6m)}</b></div>
        <div style={cell()}>Drawdown: <b>{pct(m.drawdown)}</b></div>
      </div>
      {item.replacements.length>0 && (
        <div style={{marginTop:10}}>
          <div style={{fontSize:13,color:"#374151"}}>Suggested replacements:</div>
          <div style={{display:"flex",gap:6,flexWrap:"wrap", marginTop:4}}>
            {item.replacements.map(sym=>(
              <span key={sym} style={{background:"#eff6ff",color:"#1d4ed8",padding:"2px 6px",borderRadius:6,fontSize:12}}>{sym}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
function cell(){ return {padding:8, background:"#f9fafb", borderRadius:6} as React.CSSProperties; }
export default InsightCard;
