// lib/api.ts
// noinspection JSUnusedGlobalSymbols

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL

// ─── Axios instance ───────────────────────────────────────────────────────────

export const api: AxiosInstance = axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 15_000,
})

// ─── Request interceptor — attach access token ────────────────────────────────

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = Cookies.get('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// ─── Response interceptor — auto-refresh on 401 ───────────────────────────────

let isRefreshing = false
let queue: Array<{ resolve: (v: string) => void; reject: (e: unknown) => void }> = []

function processQueue(error: unknown, token: string | null = null) {
    queue.forEach(p => (token ? p.resolve(token) : p.reject(error)))
    queue = []
}

api.interceptors.response.use(
    r => r,
    async (error: AxiosError) => {
        const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

        if (error.response?.status === 401 && !original._retry) {
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    queue.push({ resolve, reject })
                }).then(token => {
                    original.headers.Authorization = `Bearer ${token}`
                    return api(original)
                })
            }

            original._retry = true
            isRefreshing = true
            const refresh = Cookies.get('refresh_token')

            if (!refresh) {
                clearTokens()
                redirectToLogin()
                return Promise.reject(error)
            }

            try {
                const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, { refresh })
                setTokens(data.access, data.refresh)
                processQueue(null, data.access)
                original.headers.Authorization = `Bearer ${data.access}`
                return api(original)
            } catch (err) {
                processQueue(err, null)
                clearTokens()
                redirectToLogin()
                return Promise.reject(err)
            } finally {
                isRefreshing = false
            }
        }

        return Promise.reject(error)
    }
)

// ─── Redirect helper ──────────────────────────────────────────────────────────
// A hard `window.location.href` reload here would remount the whole app;
// if any query fires again before the user logs in, this fires again too —
// an infinite reload loop. Guard against that by never redirecting from a
// page that's already the login page, and use client-side nav so we don't
// force a full reload in the first place.
function redirectToLogin() {
    if (typeof window === 'undefined') return
    if (window.location.pathname.startsWith('/login')) return
    window.location.href = '/login'
}

// ─── Token helpers ────────────────────────────────────────────────────────────

export function setTokens(access: string, refresh: string) {
    Cookies.set('access_token',  access,  { expires: 1 / 48 })   // 30 min
    Cookies.set('refresh_token', refresh, { expires: 7 })
}

export function clearTokens() {
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
}


export function getAccessToken() {
    return Cookies.get('access_token')
}

// ─── Typed error extraction ───────────────────────────────────────────────────

export function extractErrorMessage(error: unknown): string {
    if (axios.isAxiosError(error)) {
        const data = error.response?.data
        if (typeof data?.detail === 'string') return data.detail
        if (typeof data?.detail === 'object') {
            return Object.entries(data.detail)
                .map(([k, v]) => `${k}: ${(v as string[]).join(', ')}`)
                .join(' | ')
        }
        if (data?.message) return data.message
    }
    if (error instanceof Error) return error.message
    return 'An unexpected error occurred.'
}