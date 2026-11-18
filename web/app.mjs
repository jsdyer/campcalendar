import {el,node,read,option,format} from "./shared.mjs";
import {bands,summarize} from "./model.mjs";
const cache=new Map();
let change=0;
function panel(park,s){
  const box=node("article");box.append(node("h2",park));
  if(!s){box.append(node("p","No matching recorded stays."));return box;}
  box.append(node("span","Median booking lead"),node("p",s.median+" days","large"),node("p","Middle half of bookings · "+s.lower+"–"+s.upper+" days ahead"),node("h3",format.format(s.count)+" reservations"));
  for(const [i,b] of s.buckets.entries()){
    const row=node("div",undefined,"barrow"),track=node("div",undefined,"track"),bar=node("i");
    bar.style.width=b.pct+"%"; track.append(bar); row.append(node("span",bands[i]),track,node("span",b.pct.toFixed(1)+"%","number"));row.title=format.format(b.n)+" reservations";box.append(row);
  }
  return box;
}
async function render(){
  const selected=++change,month=el("month").value;
  try{
    if(!cache.has(month))cache.set(month,read("month-"+month));
    const cells=await cache.get(month);
    if(selected!==change)return;
    const type=el("type").value, day=el("day").value;
    el("result").replaceChildren(...["left","right"].map(id=>panel(el(id).value,summarize(cells,el(id).value,type,day))));
    el("notice").textContent="Arrival years "+years+" · Percentages are calculated within each selection.";
  }catch{
    cache.delete(month);
    if(selected===change){el("result").replaceChildren();el("notice").textContent="Could not load this month. Choose another month or reload.";}
  }
}
let years="";
try{
 const status=await read("status"); years=status.years[0]+"–"+status.years.at(-1);
 el("count").textContent=format.format(status.count);el("stamp").textContent="Data retrieved "+status.retrieved;
 for(const p of status.parks){option("left",p,p);option("right",p,p);}
 el("left").value="Rissers Beach";el("right").value="Graves Island";option("month","All months","0");
 for(const m of status.months)option("month",new Intl.DateTimeFormat("en-CA",{month:"long",timeZone:"UTC"}).format(Date.UTC(2000,m-1,15)),m);
 document.querySelector("form").addEventListener("change",render);await render();
}catch{el("notice").textContent="The reservation snapshot is unavailable. See Sources & method.";}
