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
    WorkLogCard
} from '../worklog-card/worklog-card';

@Component({

    selector:'app-worklog-list',

    standalone:true,

    imports:[

        CommonModule,

        WorkLogCard

    ],

    templateUrl:'./worklog-list.html',

    styleUrl:'./worklog-list.scss'

})
export class WorkLogList {

    @Input()

    groups:any[]=[];

    @Output()

    open=
    new EventEmitter<any>();

    @Output()

    menu=
    new EventEmitter<{

        event:MouseEvent,

        worklog:any

    }>();

    openWorkLog(
        worklog:any
    ){

        this.open.emit(worklog);

    }

    openMenu(
        event:MouseEvent,
        worklog:any
    ){

        this.menu.emit({

            event,

            worklog

        });

    }

}
