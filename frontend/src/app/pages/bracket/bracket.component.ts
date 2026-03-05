import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LiveTournamentService } from '../../services/live-tournament.service';

@Component({
  selector: 'app-bracket',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './bracket.component.html',
})
export class BracketComponent {
  readonly bracket$;
  readonly state$;

  constructor(live: LiveTournamentService) {
    this.bracket$ = live.bracket$;
    this.state$ = live.state$;
  }

  isBracketPhase(state: any): boolean {
    const status = state?.tournament?.status;
    return status === 'top8' || status === 'done';
  }

  shortUid(uid: string) {
    return uid.length > 12 ? uid.slice(0, 6) + '…' + uid.slice(-4) : uid;
  }

  playerLabel(state: any, uid: string | null | undefined) {
    if (!uid) return '—';
    const p = (state?.players ?? []).find((x: any) => x.uid === uid);
    return p?.name ?? p?.email ?? this.shortUid(uid);
  }

  winnerLabel(state: any, m: any) {
    return m?.winnerUid ? this.playerLabel(state, m.winnerUid) : 'pending';
  }

  placeholder(code: string, bestOf: number) {
    return { code, bestOf, p1Uid: null, p2Uid: null, score1: 0, score2: 0, winnerUid: null };
  }
}
