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
    WorkLogService
} from '../../services/worklog.service';

import {
    TimelineYearModel
} from '../../models/timeline-year';

import {
    TimelineMonthModel
} from '../../models/timeline-month';

@Component({

    selector:'app-timeline',

    standalone:true,

    imports:[

        CommonModule

    ],

    templateUrl:'./timeline.html',

    styleUrl:'./timeline.scss'

})
export class Timeline
implements OnInit{

    private workLogService =
        inject(WorkLogService);

    @Input()

    visible = false;

    @Output()

    close =
    new EventEmitter<void>();

    @Output()

    weekSelected =
    new EventEmitter<number>();

    years:TimelineYearModel[]=[];

    selectedYear:number|null=null;

    months:TimelineMonthModel[]=[];

    expandedMonths = new Set<number>();


    ngOnInit():void{

        this.loadYears();

    }

    loadYears():void{

        this.workLogService
        .getTimelineYears()
        .subscribe({

            next:response=>{

                this.years =
                    response.data.years;

            }

        });

    }
loadTimeline(
    year:number
):void{

    this.selectedYear = year;

    this.expandedMonths.clear();

    this.workLogService
        .getTimeline(year)
        .subscribe({

            next:response=>{

                this.months =
                    response.data.months;

                this.months.forEach(

                    month=>{

                        this.expandedMonths.add(
                            month.month
                        );

                    }

                );

            }

        });

}

    toggleMonth(
    month:number
):void{

    if(
        this.expandedMonths.has(month)
    ){

        this.expandedMonths.delete(
            month
        );

    }
    else{

        this.expandedMonths.add(
            month
        );

    }

}

isExpanded(
    month:number
):boolean{

    return this.expandedMonths.has(
        month
    );

}


    selectWeek(
        weekOffset:number
    ):void{

        this.weekSelected.emit(
            weekOffset
        );

    }

    closeDialog():void{

        this.close.emit();

    }

}
