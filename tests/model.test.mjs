import assert from "node:assert/strict";
import test from "node:test";
import {summarize} from "../web/model.mjs";
test("missing cells are distinct from a real distribution",()=>{
 const data={P:{"RV/weekend":[3,0,0,8,2,0,1,0,0]}};
 assert.equal(summarize(data,"P","Tent","weekend"),null);
 assert.equal(summarize(data,"P","RV","weekend").median,0);
 assert.equal(summarize(data,"P","RV","weekend").buckets[2].n,1);
});
