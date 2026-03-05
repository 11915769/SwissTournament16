import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { ApiService } from '../services/api.service';
import { Auth } from '@angular/fire/auth';
import { catchError, map, of } from 'rxjs';

export const registeredGuard: CanActivateFn = () => {
  const api = inject(ApiService);
  const auth = inject(Auth);
  const router = inject(Router);

  const uid = auth.currentUser?.uid;
  if (!uid) return router.parseUrl('/login');

  return api.tournamentState().pipe(
    map(state => (state.players?.some(p => p.uid === uid) ? true : router.parseUrl('/join'))),
    catchError(() => of(router.parseUrl('/join')))
  );
};
