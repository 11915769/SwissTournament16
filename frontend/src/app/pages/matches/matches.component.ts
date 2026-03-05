import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { LiveTournamentService } from '../../services/live-tournament.service';
import { Auth } from '@angular/fire/auth';

@Component({
  selector: 'app-matches',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './matches.component.html',
})
export class MatchesComponent implements OnDestroy {
  state: any = null;
  loading = true;

  private sub?: Subscription;

  constructor(private live: LiveTournamentService, private fbAuth: Auth) {
    this.sub = this.live.state$.subscribe((s: any) => {
      this.state = s;
      this.loading = false;
    });
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }

  meUid(): string | null {
    return this.fbAuth.currentUser?.uid ?? null;
  }

  isMe(uid?: string | null): boolean {
    const me = this.meUid();
    return !!me && !!uid && uid === me;
  }

  uidToName(uid: string) {
    const p = this.state?.players?.find((x: any) => x.uid === uid);
    return p?.name ?? p?.email ?? uid.slice(0, 8);
  }

  myMatches(): any[] {
    const me = this.meUid();
    if (!me) return [];
    return (this.state?.currentMatches ?? []).filter((m: any) => m.p1Uid === me || m.p2Uid === me);
  }
}
