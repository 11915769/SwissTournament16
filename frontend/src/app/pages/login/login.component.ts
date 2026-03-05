import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  Auth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged,
  updateProfile,
} from '@angular/fire/auth';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
})
export class LoginComponent {
  // was email
  username = '';

  password = '';
  confirmPassword = ''; // new

  error: string | null = null;
  loading = false;

  constructor(private auth: Auth, private router: Router) {
    onAuthStateChanged(this.auth, (user) => {
      if (user) this.router.navigateByUrl('/tournaments');
    });
  }

  private normalizeUsername(u: string): string {
    // lower, trim, spaces -> dots, remove characters that could break email local-part
    const slug = u
      .trim()
      .toLowerCase()
      .replace(/\s+/g, '.')
      .replace(/[^a-z0-9._-]/g, '');

    return slug;
  }

  private emailFromUsername(username: string): string {
    // .invalid is a reserved TLD for testing and won’t accidentally become a real address
    return `${username}@local.invalid`;
  }

  private validateCommon() {
    this.error = null;

    const u = this.normalizeUsername(this.username);
    if (!u) {
      this.error = 'Name is required';
      return null;
    }
    if (!this.password.trim()) {
      this.error = 'Password is required';
      return null;
    }
    if (this.password.length < 6) {
      // Firebase rule for email/password
      this.error = 'Password must be at least 6 characters';
      return null;
    }

    return u;
  }

  async register() {
    const u = this.validateCommon();
    if (!u) return;

    if (!this.confirmPassword.trim()) {
      this.error = 'Please repeat the password';
      return;
    }
    if (this.password !== this.confirmPassword) {
      this.error = 'Passwords do not match';
      return;
    }

    this.loading = true;
    try {
      const email = this.emailFromUsername(u);
      const cred = await createUserWithEmailAndPassword(this.auth, email, this.password);

      // store a friendly name in Firebase user profile
      await updateProfile(cred.user, { displayName: this.username.trim() });

      await this.router.navigateByUrl('/tournaments');
    } catch (e: any) {
      this.error = e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async login() {
    const u = this.validateCommon();
    if (!u) return;

    this.loading = true;
    try {
      const email = this.emailFromUsername(u);
      await signInWithEmailAndPassword(this.auth, email, this.password);
      await this.router.navigateByUrl('/tournaments');
    } catch (e: any) {
      this.error = e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }
}
