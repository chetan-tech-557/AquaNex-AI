'use client'

import { useSyncExternalStore } from 'react'

function subscribe(onTick: () => void) {
  const id = setInterval(onTick, 1000)
  return () => clearInterval(id)
}

const getSnapshot = () => Math.floor(Date.now() / 1000) * 1000
const getServerSnapshot = () => null

/** Current time rounded to the second; `null` during server render so markup stays hydration-safe. */
export function useNow() {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}
