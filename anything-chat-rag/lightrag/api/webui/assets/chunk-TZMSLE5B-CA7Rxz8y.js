/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VUVaSldnPT06MzhlM2Y5OGE=

import{_ as n,U as o,j as l}from"./index-BRREmx1I.js";var x=n((s,t)=>{const e=s.append("rect");if(e.attr("x",t.x),e.attr("y",t.y),e.attr("fill",t.fill),e.attr("stroke",t.stroke),e.attr("width",t.width),e.attr("height",t.height),t.name&&e.attr("name",t.name),t.rx&&e.attr("rx",t.rx),t.ry&&e.attr("ry",t.ry),t.attrs!==void 0)for(const r in t.attrs)e.attr(r,t.attrs[r]);return t.class&&e.attr("class",t.class),e},"drawRect"),d=n((s,t)=>{const e={x:t.startx,y:t.starty,width:t.stopx-t.startx,height:t.stopy-t.starty,fill:t.fill,stroke:t.stroke,class:"rect"};x(s,e).lower()},"drawBackgroundRect"),g=n((s,t)=>{const e=t.text.replace(o," "),r=s.append("text");r.attr("x",t.x),r.attr("y",t.y),r.attr("class","legend"),r.style("text-anchor",t.anchor),t.class&&r.attr("class",t.class);const a=r.append("tspan");return a.attr("x",t.x+t.textMargin*2),a.text(e),r},"drawText"),h=n((s,t,e,r)=>{const a=s.append("image");a.attr("x",t),a.attr("y",e);const i=l.sanitizeUrl(r);a.attr("xlink:href",i)},"drawImage"),m=n((s,t,e,r)=>{const a=s.append("use");a.attr("x",t),a.attr("y",e);const i=l.sanitizeUrl(r);a.attr("xlink:href",`#${i}`)},"drawEmbeddedImage"),y=n(()=>({x:0,y:0,width:100,height:100,fill:"#EDF2AE",stroke:"#666",anchor:"start",rx:0,ry:0}),"getNoteRect"),p=n(()=>({x:0,y:0,width:100,height:100,"text-anchor":"start",style:"#666",textMargin:0,rx:0,ry:0,tspan:!0}),"getTextObj");export{d as a,p as b,m as c,x as d,h as e,g as f,y as g};
// TODO  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VUVaSldnPT06MzhlM2Y5OGE=
