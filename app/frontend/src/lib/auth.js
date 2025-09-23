import { writable } from 'svelte/store';

// สร้าง store สำหรับจัดการ auth state
export const authToken = writable(localStorage.getItem('token') || null);
export const currentUser = writable(null);

// ฟังก์ชันจัดการ login
export function setAuthToken(token) {
    localStorage.setItem('token', token);
    authToken.set(token);
}

// ฟังก์ชันจัดการ logout
export function clearAuth() {
    localStorage.removeItem('token');
    authToken.set(null);
    currentUser.set(null);
}

// ตรวจสอบ token
export function isAuthenticated() {
    return localStorage.getItem('token') !== null;
}