import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { ApiService } from '../../services/api.service';
import {AuthService} from '../../services/auth.service';

@Component({
  selector: 'app-join',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './join.component.html',
})
export class JoinComponent implements OnInit {
  checking = true;
  loading = false;
  error: string | null = null;
  name = '';

  constructor(
    private api: ApiService,
    private router: Router,
    private auth: AuthService,
  ) {}

  async ngOnInit() {
    this.checking = true;
    this.error = null;

    try {
      const state = await firstValueFrom(this.api.tournamentState());

      const uid = this.auth.user()?.uid ?? null;

      const already = (state.players ?? []).some((p: any) => p?.uid === uid);

      if (already) {
        await this.router.navigateByUrl('/standings');
        return;
      }
    } catch (e: any) {

    } finally {
      this.checking = false;
    }
  }

  async join() {
    const displayName = this.name.trim();
    if (!displayName) {
      this.error = 'Please enter a username';
      return;
    }

    this.loading = true;
    this.error = null;

    try {
      const res = await firstValueFrom(this.api.tournamentJoin(displayName)); // POST /tournament/join

      await this.router.navigateByUrl('/standings');
    } catch (e: any) {
      this.error = e?.error?.detail ?? e?.message ?? String(e);
    } finally {
      this.loading = false;
    }
  }
}
