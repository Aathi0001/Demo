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
    ExpenseTimelineYearModel
} from '../../models/expense-timeline-year';

import {
    ExpenseTimelineMonthModel
} from '../../models/expense-timeline-month';

@Component({

    selector:'app-expense-timeline',

    standalone:true,

    imports:[
        CommonModule
    ],

    templateUrl:'./expense-timeline.html',

    styleUrl:'./expense-timeline.scss'

})
export class ExpenseTimeline{

    @Input()

    years:ExpenseTimelineYearModel[]=[];

    @Input()

    months:ExpenseTimelineMonthModel[]=[];

    @Input()

    selectedYear:number|null=null;

    @Output()

    yearSelected=
    new EventEmitter<number>();

    @Output()

    monthSelected=
    new EventEmitter<number>();

    @Output()

    close=
    new EventEmitter<void>();

}
