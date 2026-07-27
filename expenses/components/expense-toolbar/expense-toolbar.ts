import {
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output,
    inject
} from '@angular/core';

import {
    CommonModule
} from '@angular/common';

import {
    ReactiveFormsModule,
    FormBuilder
} from '@angular/forms';

import {
    debounceTime,
    distinctUntilChanged
} from 'rxjs';

import {
    PaymentMethodOption
} from '../../../profile/models/payment-method-option';

@Component({

    selector:'app-expense-toolbar',

    standalone:true,

    imports:[
        CommonModule,
        ReactiveFormsModule
    ],

    templateUrl:'./expense-toolbar.html',

    styleUrl:'./expense-toolbar.scss'

})
export class ExpenseToolbar
implements OnInit{

    @Input()

    paymentMethods:
    PaymentMethodOption[]=[];

    @Output()

    search=
    new EventEmitter<string>();

    @Output()

    monthChange=
    new EventEmitter<string>();

    @Output()

    paymentMethodChange=
    new EventEmitter<number|null>();

    @Output()

    create=
    new EventEmitter<void>();

    private fb=
    inject(FormBuilder);

    private currentMonth=
    new Date().toISOString().substring(0,7);

    form=
    this.fb.group({

        search:[''],

        month:[this.currentMonth],

        payment_method_id:[null]

    });

    ngOnInit():void{

        this.form.controls.search.valueChanges
        .pipe(

            debounceTime(300),

            distinctUntilChanged()

        )
        .subscribe(value=>{

            this.search.emit(
                value ?? ''
            );

        });

        this.form.controls.month.valueChanges
        .subscribe(value=>{

            this.monthChange.emit(
                value ?? this.currentMonth
            );

        });

        this.form.controls.payment_method_id.valueChanges
        .subscribe(value=>{

            this.paymentMethodChange.emit(
                value
            );

        });

    }

}
