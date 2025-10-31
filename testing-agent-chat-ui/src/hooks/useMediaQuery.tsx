/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(智能测试) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(智能测试)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUhOdWF3PT06YzJlM2Y2ZGI=

import { useEffect, useState } from "react";
// @ts-expect-error  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUhOdWF3PT06YzJlM2Y2ZGI=

export function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    setMatches(media.matches);

    const listener = (e: MediaQueryListEvent) => setMatches(e.matches);
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, [query]);

  return matches;
}
