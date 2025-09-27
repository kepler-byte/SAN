import { writable } from 'svelte/store';
import { getCurrentUser } from './api.js';

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

export async function syncUserData() {
  try {
    const userData = await getCurrentUser();
    currentUser.set(userData);
    return userData;
  } catch (error) {
    console.error('Failed to sync user data:', error);
    return null;
  }
}

export function updateUserPoints(newPoints) {
  currentUser.update(user => ({
    ...user,
    points: newPoints
  }));
}