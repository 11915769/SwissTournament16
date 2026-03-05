import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { Auth } from '@angular/fire/auth';
import { authState } from 'rxfire/auth';
import { map, take } from 'rxjs/operators';

export const adminGuard: CanActivateFn = () => {
  const auth = inject(Auth);
  const router = inject(Router);

  return authState(auth).pipe(
    take(1),
    map((user) => {
      const email = (user?.email ?? '').toLowerCase();
      const admins = environment.adminEmails.map(e => e.toLowerCase());
      const ok = !!user && admins.includes(email);
      if (!ok) router.navigateByUrl('/tournaments');
      return ok;
    })
  );
};
