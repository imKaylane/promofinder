import { useState, useCallback } from 'react'
import type { AxiosError } from 'axios'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useApi<T>() {
  const [state, setState] = useState<UseApiState<T>>({ data: null, loading: false, error: null })

  const execute = useCallback(async (fn: () => Promise<{ data: T }>) => {
    setState({ data: null, loading: true, error: null })
    try {
      const { data } = await fn()
      setState({ data, loading: false, error: null })
      return data
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail: string }>
      const message = axiosErr.response?.data?.detail ?? 'Erro inesperado. Tente novamente.'
      setState({ data: null, loading: false, error: message })
      throw err
    }
  }, [])

  return { ...state, execute }
}
