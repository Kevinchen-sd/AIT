export type KeepReplaceItem = {
  symbol: string;
  as_of: string;
  action: "KEEP" | "WATCH" | "REPLACE";
  metrics: { trend_ok: boolean; r3m: number; r6m: number; drawdown: number };
  replacements: string[];
};
export type KeepReplaceResp = { as_of: string; items: KeepReplaceItem[] };
