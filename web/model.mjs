export const bands=["Same day","1–7 days","8–30 days","31–90 days","91+ days"];
export function summarize(cells,park,type,day){
  const state=cells[park]?.[type+"/"+day];
  if(!state)return null;
  const [count,lower,median,upper,...buckets]=state;
  return {count,lower,median,upper,buckets:buckets.map(n=>({n,pct:100*n/count}))};
}
