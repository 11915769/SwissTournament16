import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { ApiService } from '../../services/api.service';
import { LiveTournamentService } from '../../services/live-tournament.service';
import { AuthService } from '../../services/auth.service';
import { AdminService } from '../../services/admin.service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin.component.html',
})
export class AdminComponent {

  loading = false;
  error: string | null = null;

  state: any = null;

  constructor(
    private api: ApiService,
    private live: LiveTournamentService,
    public auth: AuthService,
    public admin: AdminService
  ) {}

  async refreshState() {
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

  async createTournament() {
    this.loading = true;
    this.error = null;

    try {
      await firstValueFrom(this.api.adminCreateTournament());
      await this.refreshState();
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
      await this.refreshState();
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
      await this.refreshState();
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
      await this.refreshState();
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
      await this.refreshState();
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
      await firstValueFrom(
        this.api.adminSetWinner(matchId, winnerUid)
      );
      await this.refreshState();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  uidToName(uid: string) {
    const p = this.state?.players?.find((x: any) => x.uid === uid);
    return p?.name ?? p?.email ?? uid.slice(0, 8);
  }
  confirmText = '';

  async deleteTournament() {
    if (this.confirmText.trim().toLowerCase() !== 'delete') {
      this.error = 'Type DELETE to confirm';
      return;
    }
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminDeleteTournament());
      this.state = null;
      this.confirmText = '';
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async clearSwissWinner(matchId: string) {
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminClearSwissWinner(matchId));
      await this.refreshState();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async resetTournament() {
    if (this.confirmText.trim().toLowerCase() !== 'delete') {
      this.error = 'Type DELETE to confirm';
      return;
    }
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminResetTournament());
      this.confirmText = '';
      await this.refreshState();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }

  }

  async removePlayer(uid: string) {
    this.loading = true;
    this.error = null;

    try {
      await firstValueFrom(this.api.adminRemovePlayer(uid));
      await this.refreshState();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async setBracketScore(m: any, score1: number, score2: number) {
    this.loading = true;
    this.error = null;
    try {
      await firstValueFrom(this.api.adminSetBracketScore(m.id, score1, score2));
      await this.refreshState();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async setWinnerAny(m: any, winnerUid: string) {
    this.loading = true;
    this.error = null;
    try {
      if (m.stage === 'bracket') {
        await firstValueFrom(this.api.adminSetBracketWinner(m.id, winnerUid));
      } else {
        await firstValueFrom(this.api.adminSetWinner(m.id, winnerUid));
      }
      await this.refreshState();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  async clearWinnerAny(m: any) {
    this.loading = true;
    this.error = null;
    try {
      if (m.stage === 'bracket') {
        await firstValueFrom(this.api.adminClearBracketWinner(m.id));
      } else {
        await firstValueFrom(this.api.adminClearSwissWinner(m.id));
      }
      await this.refreshState();
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }

  neededWins(m: any): number {
    const bo = Number(m.bestOf ?? 3);
    return Math.floor(bo / 2) + 1;
  }

}
