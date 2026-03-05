import { Component, OnDestroy } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';

import { AuthService } from '../../services/auth.service';
import { AdminService } from '../../services/admin.service';
import { LiveTournamentService } from '../../services/live-tournament.service';
import { Auth } from '@angular/fire/auth';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app-shell.component.html',
})
export class AppShellComponent implements OnDestroy {
  joined = false;

  private sub?: Subscription;

  constructor(
    public auth: AuthService,
    public admin: AdminService,
    private router: Router,
    private live: LiveTournamentService,
    private fbAuth: Auth,
  ) {
    this.sub = this.live.state$.subscribe((state) => {
      const uid = this.fbAuth.currentUser?.uid;
      this.joined = !!uid && !!state?.players?.some((p: any) => p.uid === uid);
    });
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }

  async logout() {
    await this.auth.logout();
    await this.router.navigateByUrl('/login');
  }

  getUsername(email?: string | null) {
    return email?.split('@')[0] ?? '';
  }
}
