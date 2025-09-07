import React, { useState } from "react";
import { KeepReplaceResp } from "../types";
import { InsightCard } from "../components/InsightCard";

export default function InsightsPage() {
  const [symbols, setSymbols] = useState("AAPL,MSFT,AMZN,TSLA");
  const [resp, setResp] = useState<KeepReplaceResp|null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string|null>(null);

  const run = async () => {
    setLoading(true); setErr(null);
    try {
      const r = await fetch("/v1/analysis/portfolio/keep_or_replace", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account_id: "demo", symbols: symbols.split(",").map(s=>s.trim()).filter(Boolean), benchmark: "SPY", strategy: "momo_trend@0.1.0" })
      });
      if (!r.ok) throw new Error(await r.text());
      setResp(await r.json());
    } catch (e:any) { setErr(e.message ?? "request failed"); }
    finally { setLoading(false); }
  };

  return (
    <div style={{maxWidth:900, margin:"24px auto", padding:"0 12px"}}>
      <h1 style={{fontSize:24, marginBottom:12}}>Insights</h1>
      <div style={{display:"flex", gap:8, marginBottom:12}}>
        <input style={{flex:1, border:"1px solid #e5e7eb", borderRadius:8, padding:"8px 10px"}} value={symbols} onChange={e=>setSymbols(e.target.value)} />
        <button onClick={run} disabled={loading} style={{padding:"8px 12px", borderRadius:8, background:"#000", color:"#fff"}}>
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </div>
      {err && <div style={{color:"#dc2626", marginBottom:8}}>{err}</div>}
      <div style={{display:"grid", gap:10}}>
        {resp?.items.map(it => <InsightCard key={it.symbol} item={it} />)}
      </div>
    </div>
  );
}
