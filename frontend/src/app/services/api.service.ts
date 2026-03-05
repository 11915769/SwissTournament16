import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

export type Match = {
  id: string;
  stage: 'swiss' | 'bracket';
  round: number;
  p1Uid: string;
  p2Uid: string;
  winnerUid: string | null;
  createdAt?: string;
};

export type TournamentState = {
  tournament: any;
  players: Array<{ uid: string; email?: string; name?: string | null; joinedAt?: string }>;
  playerCount: number;
  currentMatches?: Match[];
};

export interface StandingsRow {
  uid: string;
  email?: string | null;
  name?: string | null;
  wins: number;
  losses: number;
  buchholz: number;
}
@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = environment.apiBaseUrl;
  constructor(private http: HttpClient) {}

  me() { return this.http.get(`${this.base}/me`); }

  adminCreateTournament() { return this.http.post(`${this.base}/admin/create-tournament`, {}); }

  tournamentJoin(name: string) {
    return this.http.post(`${this.base}/tournament/join`, { name });
  }
  tournamentState() { return this.http.get<TournamentState>(`${this.base}/tournament/state`); }

  standings() { return this.http.get<{ standings: StandingsRow[] }>(`${this.base}/tournament/standings`); }

  adminSwissStart() { return this.http.post(`${this.base}/admin/swiss/start`, {}); }

  adminSetWinner(matchId: string, winnerUid: string) {
    return this.http.post(`${this.base}/admin/swiss/matches/${matchId}/set-winner`, { winnerUid });
  }

  adminNextRound() {
    return this.http.post(`${this.base}/admin/swiss/next-round`, {});
  }

  adminCreateTop8() {
  return this.http.post(`${this.base}/admin/bracket/create-top8`, {});
  }
  adminAdvanceBracket() {
    return this.http.post(`${this.base}/admin/bracket/advance`, {});
  }
  bracket() {
    return this.http.get<{QF:any[]; SF:any[]; F:any[]}>(`${this.base}/tournament/bracket`);
  }
  adminSetBracketWinner(matchId: string, winnerUid: string) {
    return this.http.post(`${this.base}/admin/bracket/matches/${matchId}/set-winner`, { winnerUid });
  }
  adminDeleteTournament() {
  return this.http.post(`${this.base}/admin/delete-tournament`, {});
  }
  adminClearSwissWinner(matchId: string) {
    return this.http.post(`${this.base}/admin/swiss/matches/${matchId}/clear-winner`, {});
  }

  adminClearBracketWinner(matchId: string) {
    return this.http.post(`${this.base}/admin/bracket/matches/${matchId}/clear-winner`, {});
  }
  adminResetTournament() {
  return this.http.post(`${this.base}/admin/reset-tournament`, {});
  }
  adminRemovePlayer(uid: string) {
    return this.http.post(`${this.base}/admin/players/${uid}/remove`, {});
  }
  adminSetBracketScore(matchId: string, score1: number, score2: number) {
    return this.http.post(`${this.base}/admin/bracket/matches/${matchId}/set-score`, { score1, score2 });
  }
  tournamentMe() {
    return this.http.get<{ name: string; tournamentId: string }>('/api/tournament/me');
  }
}
