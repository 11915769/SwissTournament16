import { Injectable, computed, signal } from '@angular/core';
import {
  Auth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User
} from '@angular/fire/auth';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private _user = signal<User | null>(null);
  user = computed(() => this._user());

  constructor(private auth: Auth) {
    onAuthStateChanged(this.auth, (u) => this._user.set(u));
  }

  async register(email: string, password: string) {
    return createUserWithEmailAndPassword(this.auth, email.trim(), password);
  }

  async login(email: string, password: string) {
    return signInWithEmailAndPassword(this.auth, email.trim(), password);
  }

  async logout() {
    return signOut(this.auth);
  }

  async getIdToken(): Promise<string | null> {
    const u = this.auth.currentUser;
    return u ? await u.getIdToken() : null;
  }

  getEmail(): string | null {
    return this._user()?.email ?? null;
  }

  isLoggedIn(): boolean {
    return !!this._user();
  }
}
