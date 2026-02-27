import { Component, ChangeDetectionStrategy, signal } from '@angular/core';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeaderComponent {
  isMobileMenuOpen = signal(false);

  navLinks = [
    { path: '#home', name: 'Home' },
    { path: '#about', name: 'About' },
    { path: '#projects', name: 'Projects' },
    { path: '#contact', name: 'Contact' },
  ];

  toggleMobileMenu() {
    this.isMobileMenuOpen.update(value => !value);
  }

  closeMobileMenu() {
    this.isMobileMenuOpen.set(false);
  }
}
