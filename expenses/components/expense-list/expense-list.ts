import {
    Component,
    EventEmitter,
    Input,
    Output
} from '@angular/core';

import {
    CommonModule
} from '@angular/common';

import {
    ExpenseWeek
} from '../../models/expense-list-response';

import {
    ExpenseModel
} from '../../models/expense';

@Component({

    selector:'app-expense-list',

    standalone:true,

    imports:[
        CommonModule
    ],

    templateUrl:'./expense-list.html',

    styleUrl:'./expense-list.scss'

})
export class ExpenseList{

    @Input()

    weeks:ExpenseWeek[]=[];

    @Input()

    totalCredit=0;

    @Input()

    totalDebit=0;

    @Input()

    balance=0;

    @Output()

    open=
    new EventEmitter<ExpenseModel>();

    @Output()

    menu=
    new EventEmitter<{

        event:MouseEvent,

        expense:ExpenseModel

    }>();

    openExpense(
        expense:ExpenseModel
    ){

        this.open.emit(expense);

    }

    openMenu(

        event:MouseEvent,

        expense:ExpenseModel

    ){

        this.menu.emit({

            event,

            expense

        });

    }

}
