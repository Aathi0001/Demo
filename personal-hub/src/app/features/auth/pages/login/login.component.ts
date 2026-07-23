import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ValidationErrorComponent } from '../../../../shared/components/validation-error/validation-error.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    RouterLink,
    ReactiveFormsModule,
    ValidationErrorComponent
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {

	constructor(private fb: FormBuilder) {}
	
	getErrorMessage(): string

	loginForm = this.fb.group({
	  username: [ '', [ Validators.required, Validators.minLength(3), Validators.maxLength(24) ]],
	  password: [ '', [ Validators.required, Validators.minLength(8), Validators.maxLength(24)]]
	});
	onSubmit(): void {
	  if (this.loginForm.invalid) {
	    this.loginForm.markAllAsTouched();
	    return;
	  }
	  console.log(this.loginForm.value);
	}
}
