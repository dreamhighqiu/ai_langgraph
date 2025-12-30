/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDNGcWJRPT06NjQ4OWMxMmM=

import{_ as e,l as s,H as n,e as i,I as p}from"./index-BRREmx1I.js";import{p as g}from"./treemap-75Q7IDZK-DCd2IDsw.js";import"./_baseUniq-C0xuh1ow.js";import"./_basePickBy-Da_QSuIs.js";import"./clone-CLo_8xg8.js";var v={parse:e(async r=>{const a=await g("info",r);s.debug(a)},"parse")},d={version:p.version+""},m=e(()=>d.version,"getVersion"),c={getVersion:m},l=e((r,a,o)=>{s.debug(`rendering info diagram
`+r);const t=n(a);i(t,100,400,!0),t.append("g").append("text").attr("x",100).attr("y",40).attr("class","version").attr("font-size",32).style("text-anchor","middle").text(`v${o}`)},"draw"),f={draw:l},S={parser:v,db:c,renderer:f};export{S as diagram};
// FIXME  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDNGcWJRPT06NjQ4OWMxMmM=
