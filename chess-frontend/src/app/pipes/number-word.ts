import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'numberFormat',
  standalone: true
})
export class NumberFormatPipe implements PipeTransform {

  transform(value: number | string | null | undefined, decimals: number = 2): string {
    if (value == null || value === '' || isNaN(Number(value))) {
      return '';
    }

    const num = Number(value);
    const absNum = Math.abs(num);

    if (absNum >= 1e12) {
      const formattedNum = (num / 1e12).toFixed(decimals);
      return `${parseFloat(formattedNum)}T`;
    }

    if (absNum >= 1e9) {
      const formattedNum = (num / 1e9).toFixed(decimals);
      return `${parseFloat(formattedNum)}B`;
    }

    if (absNum >= 1e6) {
      const formattedNum = (num / 1e6).toFixed(decimals);
      return `${parseFloat(formattedNum)}M`;
    }

    return new Intl.NumberFormat('en-US').format(num);
  }
}
