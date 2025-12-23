
// eslint-disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VTNKNmVnPT06OTFjMjkwZDM=

import { useState, useEffect } from 'react'

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(timer)
    }
  }, [value, delay])

  return debouncedValue
}
// @ts-expect-error  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VTNKNmVnPT06OTFjMjkwZDM=
