import React from "react";
export const Sparkline: React.FC<{ data: number[]; width?: number; height?: number; strokeWidth?: number }> = ({ data, width=120, height=36, strokeWidth=2 }) => {
  if (!data || data.length < 2) return <svg width={width} height={height} />;
  const min = Math.min(...data), max = Math.max(...data), range = max - min || 1, stepX = width / (data.length - 1);
  const points = data.map((y,i)=>`${i*stepX},${height - ((y-min)/range)*height}`).join(" ");
  const up = data[data.length - 1] >= data[0];
  return (<svg width={width} height={height}><polyline fill="none" stroke={up ? "#16a34a" : "#dc2626"} strokeWidth={strokeWidth} points={points} /></svg>);
};
