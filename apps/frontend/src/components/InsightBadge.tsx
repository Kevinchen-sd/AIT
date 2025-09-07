import React from "react";
export const InsightBadge: React.FC<{ action: "KEEP"|"WATCH"|"REPLACE" }> = ({ action }) => {
  const styles: Record<string,string> = {
    KEEP: "background:#dcfce7;color:#166534;padding:2px 6px;border-radius:6px;font-weight:600;font-size:12px",
    WATCH: "background:#fef9c3;color:#854d0e;padding:2px 6px;border-radius:6px;font-weight:600;font-size:12px",
    REPLACE: "background:#fee2e2;color:#991b1b;padding:2px 6px;border-radius:6px;font-weight:600;font-size:12px"
  };
  return <span style={{...parseInline(styles[action])}}>{action}</span>;
};
function parseInline(s: string) {
  return Object.fromEntries(s.split(";").filter(Boolean).map(kv => kv.split(":")).map(([k,v]) => [k.trim() as any, v.trim()]));
}
