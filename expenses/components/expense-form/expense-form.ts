import {
    Component,
    EventEmitter,
    Input,
    OnChanges,
    Output,
    SimpleChanges,
    inject
} from '@angular/core';

import {
    CommonModule
} from '@angular/common';

import {
    FormBuilder,
    ReactiveFormsModule,
    Validators
} from '@angular/forms';

import {
    ExpenseModel
} from '../../models/expense';

import {
    CreateExpenseRequest
} from '../../models/create-expense-request';

import {
    PaymentMethodOption
} from '../../../profile/models/payment-method-option';

@Component({

    selector:'app-expense-form',

    standalone:true,

    imports:[
        CommonModule,
        ReactiveFormsModule
    ],

    templateUrl:'./expense-form.html',

    styleUrl:'./expense-form.scss'

})
export class ExpenseForm
implements OnChanges{

    @Input()

    expense:
    ExpenseModel | null = null;

    @Input()

    paymentMethods:
    PaymentMethodOption[]=[];

    @Output()

    save=
    new EventEmitter<CreateExpenseRequest>();

    @Output()

    close=
    new EventEmitter<void>();

    private fb=
    inject(FormBuilder);

    form=
    this.fb.group({

        payment_method_id:[null],

        amount:[

            null,

            [

                Validators.required,

                Validators.min(1)

            ]

        ],

        amount_type:[

            'debit',

            Validators.required

        ],

        expense_date:[

            new Date().toISOString().substring(0,10),

            Validators.required

        ],

        notes:[

            '',

            Validators.required

        ]

    });

    ngOnChanges(
        changes:SimpleChanges
    ):void{

        if(!this.expense){

            this.form.reset({

                payment_method_id:null,

                amount:null,

                amount_type:'debit',

                expense_date:new Date().toISOString().substring(0,10),

                notes:''

            });

            return;

        }

        this.form.patchValue({

            payment_method_id:
            this.expense.payment_method_id,

            amount:
            this.expense.amount,

            amount_type:
            this.expense.amount_type,

            expense_date:
            this.expense.expense_date,

            notes:
            this.expense.notes

        });

    }

    submit():void{

        if(this.form.invalid){

            this.form.markAllAsTouched();

            return;

        }

        this.save.emit(

            this.form.getRawValue()
            as CreateExpenseRequest

        );

    }

    cancel():void{

        this.close.emit();

    }

}
