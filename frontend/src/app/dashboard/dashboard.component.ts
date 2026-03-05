import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { AuthService } from '../services/auth.service';
import { ApiService, TournamentState } from '../services/api.service';
import { AdminService } from '../services/admin.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent {
  state: TournamentState | null = null;
  email = '';
  password = '';

  loading = false;
  error: string | null = null;

  standings: any[] = [];

  bracketData: { QF: any[]; SF: any[]; F: any[] } | null = null;

  me: any = null;
  constructor(
    public auth: AuthService,
    public admin: AdminService,
    private api: ApiService
  ) {}

  private validateCreds(): boolean {
    this.error = null;
    if (!this.email.trim() || !this.password.trim()) {
      this.error = 'Email and password are required';
      return false;
    }
    if (this.password.length < 6) {
      this.error = 'Password must be at least 6 characters';
      return false;
    }
    return true;
  }

  async register() {
    if (!this.validateCreds()) return;
    this.loading = true;
    try {
      await this.auth.register(this.email, this.password);
      await this.loadMe();
    } catch (e: any) {
      this.error = e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async login() {
    if (!this.validateCreds()) return;
    this.loading = true;
    try {
      await this.auth.login(this.email, this.password);
      await this.loadMe();
    } catch (e: any) {
      this.error = e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async logout() {
    this.loading = true;
    try {
      await this.auth.logout();
      this.me = null;
      this.state = null;
    } finally {
      this.loading = false;
    }
  }

  async loadMe() {
    this.loading = true;
    this.error = null;
    try {
      this.me = await this.api.me().toPromise();
    } catch (e: any) {
      this.error = e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async createTournament() {
    this.loading = true;
    this.error = null;
    try {
      const res = await this.api.adminCreateTournament().toPromise();
      // after creation, load state
      await this.loadState();
      console.log(res);
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async joinTournament() {
    this.loading = true;
    this.error = null;
    try {
      await this.api.tournamentJoin().toPromise();
      await this.loadState();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async loadState() {
    this.loading = true;
    this.error = null;

    try {
      this.state = await firstValueFrom(this.api.tournamentState());
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }


  uidToEmail(uid: string): string {
    const p = this.state?.players?.find(x => x.uid === uid);
    return p?.email ?? uid;
  }

  async loadStandings() {
    this.loading = true;
    this.error = null;
    try {
      const res = await firstValueFrom(this.api.standings());
      this.standings = res.standings ?? [];
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async startSwiss() {
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminSwissStart());
      await this.loadState();
      await this.loadStandings();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async nextRound() {
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminNextRound());
      await this.loadState();
      await this.loadStandings();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async setWinner(matchId: string, winnerUid: string) {
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminSetWinner(matchId, winnerUid));
      await this.loadState();
      await this.loadStandings();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async loadBracket() {
    this.loading = true;
    this.error = null;
    try {
      this.bracketData = await firstValueFrom(this.api.bracket());
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async createTop8() {
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminCreateTop8());
      await this.loadBracket();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async advanceBracket() {
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminAdvanceBracket());
      await this.loadBracket();
      await this.loadState(); // optional: reflect tournament status changes
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async setBracketWinner(matchId: string, winnerUid: string) {
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminSetBracketWinner(matchId, winnerUid));
      await this.loadBracket();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }
}
