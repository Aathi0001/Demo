import {
    Component,
    HostListener,
    OnInit,
    inject
} from '@angular/core';

import {
    CommonModule
} from '@angular/common';

import {
    ChangeDetectorRef
} from '@angular/core';

import {
    ExpenseToolbar
} from '../../components/expense-toolbar/expense-toolbar';

import {
    ExpenseList
} from '../../components/expense-list/expense-list';

import {
    ExpenseForm
} from '../../components/expense-form/expense-form';

import {
    DeletePassword
} from '../../../anime/components/delete-password/delete-password';

import {
    ExpenseService
} from '../../services/expense';

import {
    ProfileService
} from '../../../profile/services/profile';

import {
    ExpenseModel
} from '../../models/expense';

import {
    ExpenseListRequest
} from '../../models/expense-list-request';

import {
    CreateExpenseRequest
} from '../../models/create-expense-request';

import {
    PaymentMethodOption
} from '../../../profile/models/payment-method-option';

@Component({

    selector:'app-expense',

    standalone:true,

    imports:[

        CommonModule,

        ExpenseToolbar,

        ExpenseList,

        ExpenseForm,

        DeletePassword

    ],

    templateUrl:'./expense.html',

    styleUrl:'./expense.scss'

})
export class Expense
implements OnInit{

    private expenseService=
    inject(ExpenseService);

    private profileService=
    inject(ProfileService);

    private cdr=
    inject(ChangeDetectorRef);

    weeks:any[]=[];

    paymentMethods:PaymentMethodOption[]=[];

    totalCredit=0;

    totalDebit=0;

    balance=0;

    month='';

    selectedExpense:
    ExpenseModel|null=null;

    openedExpense:
    ExpenseModel|null=null;

    showForm=false;

    showMenu=false;

    showDeleteDialog=false;

    isEditMode=false;

    menuX=0;

    menuY=0;

    request:ExpenseListRequest={

        search:'',

        payment_method_id:null,

        month:new Date().toISOString().substring(0,7),

        delete_status:false

    };

    ngOnInit():void{

        setTimeout(()=>{

            this.loadPaymentMethods();

            this.loadExpenses();

        });

    }

    loadPaymentMethods():void{

        this.profileService
        .paymentMethodOptions()
        .subscribe({

            next:response=>{

                this.paymentMethods=
                response.data;

            }

        });

    }

    loadExpenses():void{

        this.expenseService
        .list(this.request)
        .subscribe({

            next:response=>{

                this.month=
                response.data.month;

                this.weeks=
                response.data.weeks;

                this.totalCredit=
                response.data.summary.total_credit;

                this.totalDebit=
                response.data.summary.total_debit;

                this.balance=
                response.data.summary.balance;

                this.cdr.detectChanges();

            }

        });

    }

    create():void{

        this.selectedExpense=null;

        this.isEditMode=false;

        this.showForm=true;

    }

    closeForm():void{

        this.showForm=false;

        this.selectedExpense=null;

    }

    save(
        value:CreateExpenseRequest
    ):void{

        if(this.isEditMode){

            this.updateExpense(value);

        }

        else{

            this.createExpense(value);

        }

    }

    createExpense(
        value:CreateExpenseRequest
    ):void{

        this.expenseService
        .create(value)
        .subscribe({

            next:()=>{

                this.closeForm();

                this.loadExpenses();

            }

        });

    }

    updateExpense(
        value:CreateExpenseRequest
    ):void{

        if(!this.selectedExpense){

            return;

        }

        this.expenseService
        .update(

            this.selectedExpense.expense_id,

            value

        )
        .subscribe({

            next:()=>{

                this.closeForm();

                this.loadExpenses();

            }

        });

    }

    search(
        value:string
    ):void{

        this.request.search=value;

        this.loadExpenses();

    }

    monthChanged(
        value:string
    ):void{

        this.request.month=value;

        this.loadExpenses();

    }

    paymentMethodChanged(
        value:number|null
    ):void{

        this.request.payment_method_id=value;

        this.loadExpenses();

    }

    openExpense(
        expense:ExpenseModel
    ):void{

        this.openedExpense={

            ...expense

        };

    }

    closeExpense():void{

        this.openedExpense=null;

    }

        editExpense(): void {

        if (!this.selectedExpense) {

            return;

        }

        this.expenseService
            .detail(this.selectedExpense.expense_id)
            .subscribe({

                next: response => {

                    this.selectedExpense =
                        response.data;

                    this.isEditMode = true;

                    this.showForm = true;

                    this.closeMenu();

                    this.cdr.detectChanges();

                }

            });

    }

    openMenu(
        data: any
    ): void {

        data.event.preventDefault();

        this.selectedExpense =
            data.expense;

        this.menuX =
            data.event.clientX;

        this.menuY =
            data.event.clientY;

        this.showMenu = true;

    }

    closeMenu(): void {

        this.showMenu = false;

    }

    deleteExpense(): void {

        if (!this.selectedExpense) {

            return;

        }

        this.expenseService
            .scheduleDelete(
                this.selectedExpense.expense_id
            )
            .subscribe({

                next: () => {

                    this.closeMenu();

                    this.openedExpense = null;

                    this.loadExpenses();

                }

            });

    }

    restoreExpense(): void {

        if (!this.selectedExpense) {

            return;

        }

        this.expenseService
            .restore(
                this.selectedExpense.expense_id
            )
            .subscribe({

                next: () => {

                    this.closeMenu();

                    this.loadExpenses();

                }

            });

    }

    openDeleteDialog(): void {

        this.showDeleteDialog = true;

        this.closeMenu();

        this.cdr.detectChanges();

    }

    closeDeleteDialog(): void {

        this.showDeleteDialog = false;

    }

    permanentDelete(
        password: string
    ): void {

        if (!this.selectedExpense) {

            return;

        }

        this.expenseService
            .permanentDelete(

                this.selectedExpense.expense_id,

                {

                    delete_password: password

                }

            )
            .subscribe({

                next: () => {

                    this.closeDeleteDialog();

                    this.closeMenu();

                    this.openedExpense = null;

                    this.loadExpenses();

                }

            });

    }

    @HostListener(
        'document:click',
        ['$event']
    )
    closeContextMenu(
        event: MouseEvent
    ): void {

        const target =
            event.target as HTMLElement;

        if (

            target.closest('.expense-menu') ||

            target.closest('.menu-btn')

        ) {

            return;

        }

        this.showMenu = false;

    }

}
